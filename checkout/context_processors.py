from .models import Cart


def cart_total(request):
    """Context processor to get the total number of items in the user's cart."""
    total_items = 0
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)  
        total_items = cart.items.count() if cart else 0  
    return {'cart_total': total_items}
