from django.urls import path
from . import views

app_name = 'checkout'

urlpatterns = [
    path("pricing/", views.pricing, name="pricing"),
    path("", views.checkout, name="checkout"),
    path("add-to-cart/<int:session_id>/",
         views.add_to_cart, name="add_to_cart"),
    path("cart/", views.view_cart, name="view_cart"),
    path('cart-total/', views.cart_total_view, name='cart_total'),
    path('cart-contents/', views.cart_contents_view, name='cart_contents'),
    path("create-checkout-session/", views.create_checkout_session,
         name="create_checkout_session"),
    path("success/<order_number>/",
         views.checkout_success, name="checkout_success"),
    path("cancel/", views.payment_cancel, name="payment_cancel"),
    path("cache_checkout_data/", views.cache_checkout_data,
         name="cache_checkout_data"),
    path("increase_quantity/<int:item_id>/",
         views.increase_quantity, name="increase_quantity"),
    path("decrease_quantity/<int:item_id>/",
         views.decrease_quantity, name="decrease_quantity"),
    path("remove_from_cart/<int:item_id>/",
         views.remove_from_cart, name="remove_from_cart"),
    path("wh/", views.stripe_webhook, name="stripe_webhook"),
]
