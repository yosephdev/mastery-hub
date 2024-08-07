from django.urls import path
from . import views
from .views import (
    pricing,
    increase_quantity,
    decrease_quantity,
    remove_from_cart,
)
from masteryhub.views import (
    session_list,
)
from .webhooks import stripe_webhook

urlpatterns = [
    path("pricing/", pricing, name="pricing"),
    path("", views.checkout, name="checkout"),
    path("add-to-cart/<int:session_id>/", views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="view_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path(
        "create-checkout-session/",
        views.create_checkout_session,
        name="create_checkout_session",
    ),
    path("success/", views.checkout_success, name="checkout_success"),
    path("cancel/", views.payment_cancel, name="payment_cancel"),
    path(
        "checkout/success/<order_number>/",
        views.checkout_success,
        name="checkout_success",
    ),
    path("cache_checkout_data/", views.cache_checkout_data, name="cache_checkout_data"),
    path(
        "increase_quantity/<int:item_id>/", increase_quantity, name="increase_quantity"
    ),
    path(
        "decrease_quantity/<int:item_id>/", decrease_quantity, name="decrease_quantity"
    ),
    path("remove_from_cart/<int:item_id>/", remove_from_cart, name="remove_from_cart"),
    path('webhook/stripe/', stripe_webhook, name='stripe_webhook'),
]
