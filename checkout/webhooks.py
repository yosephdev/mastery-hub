from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
import stripe
from django.conf import settings
from .webhook_handler import StripeWH_Handler

import logging

logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
def stripe_webhook(request):
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None

    logger.info(f"Received webhook payload: {payload}")
    logger.info(f"Received signature header: {sig_header}")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
        )
        logger.info(f"Successfully constructed event: {event['type']}")
    except ValueError as e:
        logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"Invalid signature: {str(e)}")
        return HttpResponse(status=400)

    logger.info(f"Received webhook event: {event['type']}")

    handler = StripeWH_Handler(request)

    event_map = {
        "payment_intent.succeeded": handler.handle_payment_intent_succeeded,
        "payment_intent.payment_failed": handler.handle_payment_intent_payment_failed,
    }

    event_type = event["type"]
    event_handler = event_map.get(event_type, handler.handle_event)

    try:
        response = event_handler(event)
        logger.info(f"Handled event {event_type} successfully")
        return response
    except Exception as e:
        logger.error(f"Error handling event {event_type}: {str(e)}")
        return HttpResponse(status=500)
