from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views import View
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Q, Count, Sum
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from .models import (
    Payment,
    Cart,
    CartItem,
    Order,
)
from accounts.models import (
    Profile,
)
from masteryhub.models import (
    Session,
    Category,
)
from checkout.forms import OrderForm
import stripe
import json
import logging

# Create your views here.


def pricing(request):
    """A view that handles pricing."""
    return render(request, "checkout/pricing.html")


def session_list(request):
    """A view that renders the list of sessions with optional filtering."""
    query = request.GET.get("q")
    selected_category = request.GET.get("category")

    sessions = Session.objects.filter(status="scheduled")

    if query:
        sessions = sessions.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    if selected_category:
        sessions = sessions.filter(category__name=selected_category)

    categories = Category.objects.all()

    for session in sessions:
        print(f"Session ID: {session.id}, Price: {session.price}")

    context = {
        "sessions": sessions,
        "categories": categories,
        "selected_category": selected_category,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    }

    return render(request, "masteryhub/session_list.html", context)


@login_required
def add_to_cart(request, session_id):
    """A view that adds a session to the user's cart."""
    if request.method == "POST":
        session = get_object_or_404(Session, id=session_id)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, session=session)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        total = sum(
            item.session.price * item.quantity for item in cart.cartitem_set.all()
        )
        messages.success(request, f"Added {session.title} to your cart.")
        return JsonResponse({"success": True, "total": float(total)})
    messages.error(request, "Failed to add session to cart.")
    return JsonResponse({"success": False})


@login_required
def view_cart(request):
    """A view that renders the user's cart."""
    cart = get_object_or_404(Cart, user=request.user)
    return render(request, "checkout/cart.html", {"cart": cart})


@login_required
def checkout(request):
    """A view that handles the checkout process."""
    cart = get_object_or_404(Cart, user=request.user)
    price = request.GET.get("price")
    if price:
        grand_total = float(price)
    else:
        grand_total = sum(
            item.session.price * item.quantity for item in cart.cartitem_set.all()
        )

    MIN_CHARGE_AMOUNT = 50

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            full_name = form.cleaned_data["full_name"]
            street_address1 = form.cleaned_data["address"]
            street_address2 = form.cleaned_data.get("address2", "")
            county = form.cleaned_data.get("county", "")
            town_or_city = form.cleaned_data["city"]
            postcode = form.cleaned_data.get("postcode", "")
            country = form.cleaned_data["country"]
            phone_number = request.POST.get("phone_number", "")

            order = Order(
                user=request.user,
                order_number="ORD" + str(int(grand_total * 1000)),
                full_name=full_name,
                street_address1=street_address1,
                street_address2=street_address2,
                county=county,
                town_or_city=town_or_city,
                postcode=postcode,
                country=country,
                phone_number=phone_number,
                order_total=grand_total,
                delivery_cost=0,
                grand_total=grand_total,
            )
            order.save()

            payment = Payment.objects.create(
                user=request.user.profile, amount=grand_total, session=None
            )

            cart.cartitem_set.all().delete()

            messages.success(
                request,
                "Your purchase was successful. A confirmation email has been sent to you.",
            )
            return redirect("checkout_success", order_number=order.order_number)
        else:
            messages.error(
                request,
                "There was an error with your order. Please check your details and try again.",
            )
    else:
        form = OrderForm()

    if grand_total * 100 >= MIN_CHARGE_AMOUNT:
        intent = stripe.PaymentIntent.create(
            amount=int(grand_total * 100),
            currency="usd",
            metadata={"integration_check": "accept_a_payment"},
        )
        client_secret = intent.client_secret
    else:
        setup_intent = stripe.SetupIntent.create(
            usage="off_session", payment_method_types=["card"]
        )
        client_secret = setup_intent.client_secret

    context = {
        "order_form": form,
        "client_secret": client_secret,
        "cart": cart,
        "grand_total": grand_total,
        "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
    }
    return render(request, "checkout/checkout.html", context)


@login_required
def create_checkout_session(request):
    """A view that creates a Stripe Checkout session."""
    cart = get_object_or_404(Cart, user=request.user)
    line_items = []

    for item in cart.cartitem_set.all():
        line_items.append(
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": item.session.title,
                    },
                    "unit_amount": int(item.session.price * 100),
                },
                "quantity": item.quantity,
            }
        )

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=line_items,
            mode="payment",
            success_url=request.build_absolute_uri("/checkout/checkout_success/"),
            cancel_url=request.build_absolute_uri("/checkout/payment_cancel/"),
        )
    except stripe.error.InvalidRequestError as e:
        return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"id": checkout_session.id})


@login_required
def payment_cancel(request):
    """A view that handles the payment cancellation."""
    return render(request, "checkout/payment_cancel.html")


def complete_purchase(request):
    """A view that handles the purhase complete."""
    return render(request, "checkout/purchase_complete.html")


@require_POST
def cache_checkout_data(request):
    try:
        client_secret = request.POST.get("client_secret")
        if not client_secret:
            raise ValueError("Missing client_secret")

        pid = client_secret.split("_secret")[0]
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.PaymentIntent.modify(
            pid,
            metadata={
                "cart": json.dumps(request.session.get("cart", {})),
                "save_info": request.POST.get("save_info"),
                "username": request.user.username,
            },
        )
        return HttpResponse(status=200)
    except Exception as e:
        logger.error(f"Error modifying PaymentIntent: {e}")
        messages.error(
            request,
            "Sorry, your payment cannot be processed right now. Please try again later.",
        )
        return HttpResponse(content=str(e), status=400)


def checkout_view(request):
    cart = get_cart(request)
    total = int(cart.total * 100)

    payment_intent = stripe.PaymentIntent.create(
        amount=total,
        currency="usd",
    )

    return render(
        request,
        "checkout/checkout.html",
        {
            "client_secret": payment_intent.client_secret,
            "stripe_public_key": settings.STRIPE_PUBLIC_KEY,
            "cart": cart,
            "grand_total": cart.total,
        },
    )


@login_required
def checkout_success(request, order_number):
    """Handle successful checkouts."""
    order = get_object_or_404(Order, order_number=order_number)
    context = {
        "order": order,
        "from_profile": False,
    }
    return render(request, "checkout/checkout_success.html", context)


@require_POST
def increase_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.quantity += 1
    cart_item.save()
    return redirect("view_cart")


@require_POST
def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    return redirect("view_cart")


@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()
    messages.success(request, f"Removed {cart_item.session.title} from your cart.")
    return redirect("view_cart")
