from decimal import Decimal
from django.conf import settings
from .models import Cart


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
