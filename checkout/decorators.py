from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

def cart_action_handler(action_type):
    """Decorator for cart actions with error handling and logging."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            try:
                with transaction.atomic():
                    result = view_func(request, *args, **kwargs)
                    logger.info(
                        f"Cart {action_type} successful for user {request.user.id}")
                    return result
            except ValidationError as e:
                logger.warning(
                    f"Cart {action_type} validation error for user {request.user.id}: {str(e)}")
                messages.error(request, str(e))
            except Exception as e:
                logger.error(
                    f"Cart {action_type} error for user {request.user.id}: {str(e)}")
                messages.error(
                    request, "An unexpected error occurred. Please try again.")
            return redirect('checkout:view_cart')
        return _wrapped_view
    return decorator 