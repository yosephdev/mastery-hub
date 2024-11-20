from .models import Cart


def cart_total(request):
    """Context processor to get the total number of items in the user's cart."""
    total_items = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()  
        if cart:
            total_items = cart.items.count() 
    return {'cart_total': total_items}
