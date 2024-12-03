from decimal import Decimal
from django.conf import settings
from .models import Cart


def cart_contents(request):
    """
    Context processor for making cart contents available across all templates.
    """
    cart_items = []
    total = Decimal('0.00')
    item_count = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.all()
            total = cart.get_total_price()
            item_count = cart_items.count()
        except Cart.DoesNotExist:
            pass

    delivery_fee = Decimal(settings.STANDARD_DELIVERY_FEE)
    grand_total = total + delivery_fee if total < settings.FREE_DELIVERY_THRESHOLD else total

    context = {
        'cart_items': cart_items,
        'total': total,
        'item_count': item_count,
        'delivery': delivery_fee,
        'free_delivery_threshold': settings.FREE_DELIVERY_THRESHOLD,
        'grand_total': grand_total,
    }

    return context
