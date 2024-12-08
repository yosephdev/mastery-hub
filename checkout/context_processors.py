from decimal import Decimal
from .models import Cart
from django.contrib import messages

def message_processor(request):
    """Clear messages after they're displayed"""
    storage = messages.get_messages(request)
    to_return = []

    for message in storage:
        to_return.append({
            'message': message.message,
            'level': message.level,
            'tags': message.tags,
        })

    storage.used = True
    return {'messages': to_return}


def cart_contents(request):
    """
    Context processor to make cart contents available across all templates
    """
    cart_total = Decimal('0.00')
    cart_items_count = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.prefetch_related('items').get(user=request.user)
            cart_total = cart.get_total_price()
            cart_items_count = cart.items.count()
        except Cart.DoesNotExist:
            pass

    return {
        'cart_total': cart_total,
        'cart_items_count': cart_items_count,
        'cart': cart if request.user.is_authenticated and 'cart' in locals() else None
    }


def project_context(request):
    """
    Add project-wide context variables
    """
    return {
        'PROJECT_NAME': 'Mastery Hub',
        'CURRENT_PATH': request.path
    }