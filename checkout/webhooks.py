from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import stripe
from django.conf import settings
from .webhook_handler import StripeWH_Handler
import json
import logging
from .models import Order, OrderLineItem
from profiles.models import Profile
from masteryhub.models import Session
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
def stripe_webhook(request):
    wh_secret = settings.STRIPE_WH_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, wh_secret)
    except ValueError:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object
        try:
            order = Order.objects.get(stripe_pid=payment_intent.id)
            if not order.webhook_processed:
                if order.payment_status != 'COMPLETED':
                    order.payment_status = 'COMPLETED'
                    order.status = 'completed'
                    order.webhook_processed = True
                    order.save()

                    if not order.confirmation_email_sent:
                        send_order_confirmation(order.id)
                        order.confirmation_email_sent = True
                        order.save()

                    logger.info(
                        f"Order {order.order_number} marked as completed and confirmation email sent.")
            else:
                logger.debug(
                    f"Order {order.order_number} already processed via webhook.")

        except Order.DoesNotExist:
            logger.error(
                f"Order not found for PaymentIntent {payment_intent.id}")

    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        try:
            order = Order.objects.get(stripe_pid=payment_intent.id)
            if order.webhook_processed:
                order.payment_status = 'FAILED'
                order.save()
                logger.warning(f"Order {order.order_number} marked as failed.")
        except Order.DoesNotExist:
            logger.error(
                f"Order not found for PaymentIntent {payment_intent.id}")

    return HttpResponse(status=200)


class StripeWH_Handler:
    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        cust_email = order.email
        subject = render_to_string(
            'checkout/confirmation_emails/confirmation_email_subject.txt',
            {'order': order})
        body = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL})

        send_mail(
            subject=subject,
            message=strip_tags(body),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[cust_email],
            html_message=body
        )

    def handle_event(self, event):
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        intent = event.data.object
        pid = intent.id
        cart = intent.metadata.cart
        save_info = intent.metadata.save_info

        stripe_charge = stripe.Charge.retrieve(intent.latest_charge)
        billing_details = stripe_charge.billing_details
        shipping_details = intent.shipping
        grand_total = round(stripe_charge.amount / 100, 2)

        # Clean data in the shipping details
        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        profile = None
        username = intent.metadata.username
        if username != 'AnonymousUser':
            profile = Profile.objects.get(user__username=username)
            if save_info:
                profile.phone_number = shipping_details.phone
                profile.save()

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=shipping_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=shipping_details.phone,
                    country__iexact=shipping_details.address.country,
                    postcode__iexact=shipping_details.address.postal_code,
                    town_or_city__iexact=shipping_details.address.city,
                    street_address1__iexact=shipping_details.address.line1,
                    street_address2__iexact=shipping_details.address.line2,
                    county__iexact=shipping_details.address.state,
                    grand_total=grand_total,
                    original_cart=cart,
                    stripe_pid=pid,
                )
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)

        if order_exists:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database',
                status=200)

        order = None
        try:
            order = Order.objects.create(
                full_name=shipping_details.name,
                user_profile=profile,
                email=billing_details.email,
                phone_number=shipping_details.phone,
                country=shipping_details.address.country,
                postcode=shipping_details.address.postal_code,
                town_or_city=shipping_details.address.city,
                street_address1=shipping_details.address.line1,
                street_address2=shipping_details.address.line2,
                county=shipping_details.address.state,
                original_cart=cart,
                stripe_pid=pid,
            )
            for item_id, item_data in json.loads(cart).items():
                session = Session.objects.get(id=item_id)
                if isinstance(item_data, int):
                    order_line_item = OrderLineItem(
                        order=order,
                        session=session,
                        quantity=item_data,
                        price=session.price
                    )
                    order_line_item.save()
                else:
                    for size, quantity in item_data['items_by_size'].items():
                        order_line_item = OrderLineItem(
                            order=order,
                            session=session,
                            quantity=quantity,
                            price=session.price
                        )
                        order_line_item.save()
        except Exception as e:
            if order:
                order.delete()
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {e}',
                status=500)

        self._send_confirmation_email(order)
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
            status=200)

    def handle_payment_intent_payment_failed(self, event):
        return HttpResponse(
            content=f'Webhook received: {event["type"]}',
            status=200)


def send_order_confirmation(order_id):
    """
    Send an order confirmation email for the given order ID.
    """
    try:
        order = Order.objects.get(id=order_id)
        if not order.confirmation_email_sent:
            subject = render_to_string(
                'checkout/confirmation_emails/confirmation_email_subject.txt',
                {'order': order}
            )
            body = render_to_string(
                'checkout/confirmation_emails/confirmation_email_body.txt',
                {'order': order, 'contact_email': settings.DEFAULT_FROM_EMAIL}
            )

            send_mail(
                subject=subject,
                message=strip_tags(body),
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.email],
                html_message=body,
                fail_silently=False
            )

            order.confirmation_email_sent = True
            order.save()
            logger.info(
                f"Confirmation email sent successfully for order {order.order_number}")
    except Order.DoesNotExist:
        logger.error(
            f"Order with ID {order_id} not found for sending confirmation email.")
    except Exception as e:
        logger.error(
            f"Failed to send confirmation email for order {order_id}: {str(e)}")
