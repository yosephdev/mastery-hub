from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse, JsonResponse
import stripe
from django.conf import settings
from .webhook_handler import StripeWH_Handler
import json
import logging

logger = logging.getLogger(__name__)


@require_POST
@csrf_exempt
def stripe_webhook(request):
    """
    Listen for webhooks from Stripe
    """
    # Setup
    wh_secret = settings.STRIPE_WH_SECRET
    stripe.api_key = settings.STRIPE_SECRET_KEY

    # Get the webhook data and verify its signature
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    event = None

    try:
        # Log the raw payload for debugging
        logger.info(f"Webhook received with signature: {sig_header}")
        
        # Construct the event with the payload and signature
        event = stripe.Webhook.construct_event(
            payload, sig_header, wh_secret
        )
        logger.info(f"Successfully constructed event: {event['type']}")
    except ValueError as e:
        # Invalid payload
        logger.error(f"Invalid payload: {str(e)}")
        return HttpResponse(content=f"Invalid payload: {str(e)}", status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        logger.error(f"Invalid signature: {str(e)}")
        return HttpResponse(content=f"Invalid signature: {str(e)}", status=400)
    except Exception as e:
        # Generic error
        logger.error(f"Webhook error: {str(e)}")
        return HttpResponse(content=f"Webhook error: {str(e)}", status=400)

    # Set up a webhook handler
    handler = StripeWH_Handler(request)

    # Map webhook events to relevant handler functions
    event_map = {
        "payment_intent.succeeded": handler.handle_payment_intent_succeeded,
        "payment_intent.payment_failed": handler.handle_payment_intent_payment_failed,
        "checkout.session.completed": handler.handle_payment_intent_succeeded,
        "charge.succeeded": handler.handle_payment_intent_succeeded,
    }

    # Get the webhook type from Stripe
    event_type = event["type"]

    # If there's a handler for it, get it from the event map
    # Use the generic one by default
    event_handler = event_map.get(event_type, handler.handle_event)

    try:
        # Call the event handler with the event
        response = event_handler(event)
        logger.info(f"Webhook handled successfully: {event_type}")
        return response
    except Exception as e:
        logger.error(f"Error handling webhook: {str(e)}")
        return HttpResponse(
            content=f"Webhook handler error: {str(e)}",
            status=500,
        )
