from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
import stripe
from django.conf import settings
from .webhook_handler import StripeWH_Handler
import json
import logging
from .models import Order
from .tasks import send_order_confirmation, send_payment_failure_email

logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
def stripe_webhook(request):
    wh_secret = settings.STRIPE_WH_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']

    try:
        event = stripe.Webhook.construct_event(payload, sig_header, wh_secret)
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
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
                        send_order_confirmation.delay(order.id)
                        order.confirmation_email_sent = True
                        order.save()

                    logger.info(f"Order {order.order_number} marked as completed and confirmation email sent.")
            else:
                logger.debug(f"Order {order.order_number} already processed via webhook.")

        except Order.DoesNotExist:
            logger.error(f"Order not found for PaymentIntent {payment_intent.id}")

    elif event.type == 'payment_intent.payment_failed':
        payment_intent = event.data.object
        try:
            order = Order.objects.get(stripe_pid=payment_intent.id)
            if order.webhook_processed:
                order.payment_status = 'FAILED'
                order.save()
                send_payment_failure_email.delay(order.id)
                logger.warning(f"Order {order.order_number} marked as failed.")
        except Order.DoesNotExist:
            logger.error(f"Order not found for PaymentIntent {payment_intent.id}")

    return HttpResponse(status=200)
