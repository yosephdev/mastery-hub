from checkout.models import Cart

def cart_total(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        total = sum(item.session.price * item.quantity for item in cart.cartitem_set.all())
        return {'grand_total': total}
    return {'grand_total': 0}