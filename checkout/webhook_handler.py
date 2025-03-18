from django.http import HttpResponse
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import stripe
import logging
from masteryhub.models import Session
from checkout.models import Order, Payment
from profiles.models import Profile
import time

logger = logging.getLogger(__name__)
stripe.api_key = settings.STRIPE_SECRET_KEY


class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def _send_confirmation_email(self, order):
        """
        Send the user a confirmation email.
        Logs any errors during email sending.
        """
        # Check if the order has a confirmation_email_sent field and it's True
        # This is to prevent duplicate emails
        if hasattr(order, 'confirmation_email_sent') and order.confirmation_email_sent:
            logger.info(f"Confirmation email already sent for order {order.order_number}")
            return
            
        try:
            # Use the task function directly
            from .tasks import send_order_confirmation
            send_order_confirmation(order.id)
        except Exception as e:
            logger.error(
                f"Failed to send confirmation email for order {order.order_number}: {str(e)}")

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event.
        Logs unhandled events for debugging.
        """
        logger.info(f"Unhandled webhook received: {event['type']}")
        return HttpResponse(
            content=f'Webhook received: {event["type"]}', status=200
        )

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe.
        """
        intent = event.data.object
        pid = intent.id
        session_id = intent.metadata.get('session_id')
        save_info = intent.metadata.get('save_info', False)

        try:
            stripe_charge = stripe.Charge.retrieve(intent.latest_charge)
            billing_details = stripe_charge.billing_details
            grand_total = round(stripe_charge.amount / 100, 2)
        except Exception as e:
            logger.error(
                f"Error retrieving Stripe charge for PaymentIntent {pid}: {str(e)}")
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: Failed to retrieve charge',
                status=500,
            )

        profile = None
        username = intent.metadata.get('username')
        if username and username != "AnonymousUser":
            try:
                profile = Profile.objects.get(user__username=username)
                if save_info:
                    profile.default_phone_number = billing_details.phone
                    profile.default_country = billing_details.address.country
                    profile.default_postcode = billing_details.address.postal_code
                    profile.default_town_or_city = billing_details.address.city
                    profile.default_street_address1 = billing_details.address.line1
                    profile.default_street_address2 = billing_details.address.line2
                    profile.default_county = billing_details.address.state
                    profile.save()
            except Profile.DoesNotExist:
                logger.warning(f"Profile not found for username: {username}")
            except Exception as e:
                logger.error(
                    f"Error updating profile for username {username}: {str(e)}")

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(
                    full_name__iexact=billing_details.name,
                    email__iexact=billing_details.email,
                    phone_number__iexact=billing_details.phone,
                    country__iexact=billing_details.address.country,
                    postcode__iexact=billing_details.address.postal_code,
                    town_or_city__iexact=billing_details.address.city,
                    street_address1__iexact=billing_details.address.line1,
                    street_address2__iexact=billing_details.address.line2,
                    county__iexact=billing_details.address.state,
                    order_total=grand_total,
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
                status=200,
            )

        # Initialize order variable to None before trying to create it
        order = None
        try:
            order = Order.objects.create(
                full_name=billing_details.name,
                user=profile.user if profile else None,
                email=billing_details.email,
                phone_number=billing_details.phone,
                country=billing_details.address.country,
                postcode=billing_details.address.postal_code,
                town_or_city=billing_details.address.city,
                street_address1=billing_details.address.line1,
                street_address2=billing_details.address.line2,
                county=billing_details.address.state,
                stripe_pid=pid,
                order_total=grand_total,
                delivery_cost=0,
            )
            if session_id:
                try:
                    session = Session.objects.get(id=session_id)
                    Payment.objects.create(
                        user=profile,
                        amount=grand_total,
                        session=session,
                    )
                except Session.DoesNotExist:
                    logger.error(f"Session not found for session_id: {session_id}")
                    if order:
                        order.delete()
                    return HttpResponse(
                        content=f'Webhook received: {event["type"]} | ERROR: Session not found',
                        status=500,
                    )
        except Exception as e:
            logger.error(
                f"Error creating order for PaymentIntent {pid}: {str(e)}")
            if order:
                order.delete()
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: {str(e)}',
                status=500,
            )

        # Only send confirmation email if order was successfully created
        if order:
            self._send_confirmation_email(order)
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook',
                status=200,
            )
        else:
            return HttpResponse(
                content=f'Webhook received: {event["type"]} | ERROR: Failed to create order',
                status=500,
            )

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        intent = event.data.object
        pid = intent.id
        
        logger.warning(f"Payment failed for PaymentIntent {pid}")
        
        # Find the order associated with this payment intent
        try:
            order = Order.objects.get(stripe_pid=pid)
            order.payment_status = 'FAILED'
            order.save()
            
            # Send email notification about failed payment
            from .tasks import send_payment_failure_email
            send_payment_failure_email(order.id)
            
            logger.info(f"Order {order.order_number} marked as failed payment")
            
        except Order.DoesNotExist:
            logger.warning(f"No order found for failed PaymentIntent {pid}")
        except Exception as e:
            logger.error(f"Error handling payment failure for PaymentIntent {pid}: {str(e)}")
        
        return HttpResponse(
            content=f'Webhook received: {event["type"]} | SUCCESS: Payment failure recorded',
            status=200
        )
