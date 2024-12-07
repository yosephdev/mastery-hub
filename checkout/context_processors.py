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
    Context processor for making cart contents available across all templates.
    """
    cart_items = []
    total = 0
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.select_related('session').all()
            total = cart.get_total_price()
        except Cart.DoesNotExist:
            pass

    return {
        'cart_items': cart_items,
        'total': total,
    }
