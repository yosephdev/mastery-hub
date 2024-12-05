from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import re
import os
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.http import JsonResponse
import logging
import uuid
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db import transaction

from profiles.models import Profile
from masteryhub.models import Session
from .models import Order, CartItem, Cart, OrderLineItem

User = get_user_model()

logger = logging.getLogger(__name__)

stripe.api_key = settings.STRIPE_SECRET_KEY


def validate_phone(value):
    if not re.match(r'^\+?1?\d{9,15}$', value):
        raise ValidationError(
            'Phone number must be in the format: "+999999999". Up to 15 digits allowed.'
        )


def validate_postal_code(value):
    if not re.match(r'^\d{5}(?:[-\s]\d{4})?$', value):
        raise ValidationError(
            'Postal code must be in the format: "12345" or "12345-6789".'
        )


class SessionForm(forms.ModelForm):
    """
    Form class for handling session information in the checkout process.
    """

    class Meta:
        model = Session
        fields = [
            "title",
            "description",
            "duration",
            "category",
            "max_participants",
            "price",
        ]
        widgets = {
            "date": forms.DateTimeInput(
                attrs={"type": "datetime-local", "class": "form-control"}
            ),
            "duration": forms.TimeInput(
                attrs={"type": "time", "class": "form-control"}
            ),
            "price": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }


class OrderForm(forms.ModelForm):
    """
    Form class for handling order information in the checkout process.
    """

    class Meta:
        model = Order
        fields = (
            "full_name",
            "email",
            "phone_number",
            "street_address1",
            "street_address2",
            "town_or_city",
            "postcode",
            "country",
            "county",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "full_name": "Full Name",
            "email": "Email Address",
            "phone_number": "Phone Number",
            "postcode": "Postal Code",
            "town_or_city": "Town or City",
            "street_address1": "Street Address 1",
            "street_address2": "Street Address 2",
            "county": "County, State or Locality",
        }

        self.fields["full_name"].widget.attrs["autofocus"] = True
        for field in self.fields:
            if field != "country":
                placeholder = placeholders.get(field, field)
                if self.fields[field].required:
                    placeholder += " *"
                self.fields[field].widget.attrs["placeholder"] = placeholder
            self.fields[field].widget.attrs["class"] = "border-black rounded-0 profile-form-input"
            self.fields[field].label = False

        self.fields['phone_number'].validators.append(validate_phone)
        self.fields['postcode'].validators.append(validate_postal_code)


class CheckoutForm(forms.Form):
    phone_number = forms.CharField(validators=[validate_phone])
    postal_code = forms.CharField(validators=[validate_postal_code])


class ProfileForm(forms.ModelForm):
    mentor_since = forms.DateField(widget=forms.SelectDateWidget())

    def clean_mentor_since(self):
        mentor_since = self.cleaned_data.get('mentor_since')
        if mentor_since and mentor_since > timezone.now().date():
            raise ValidationError(
                "The 'Mentor Since' date cannot be in the future.")
        return mentor_since


def pricing(request):
    """A view that displays pricing information."""
    pricing_plans = [
        {
            'name': 'Basic',
            'price': 9.99,
            'features': [
                'Access to 5 sessions per month',
                'Basic mentorship features',
                'Email support'
            ],
            'button_class': 'btn-outline-dark'
        },
        {
            'name': 'Pro',
            'price': 19.99,
            'features': [
                'Access to 15 sessions per month',
                'Advanced mentorship features',
                'Priority email support'
            ],
            'button_class': 'btn-success'
        },
        {
            'name': 'Enterprise',
            'price': 49.99,
            'features': [
                'Unlimited access to sessions',
                'Premium mentorship features',
                '24/7 phone and email support'
            ],
            'button_class': 'btn-info'
        }
    ]

    context = {
        'pricing_plans': pricing_plans
    }

    return render(request, 'checkout/pricing.html', context)


@login_required
@require_POST
def increase_quantity(request, item_id):
    cart_item = get_object_or_404(
        CartItem, id=item_id, cart__user=request.user)
    if not cart_item.session.is_full():
        cart_item.quantity += 1
        cart_item.save()
        messages.success(
            request, f"Increased quantity for {cart_item.session.title}.")
    else:
        messages.error(request, "Cannot add more. The session is full.")
    return redirect('checkout:view_cart')


@login_required
@require_POST
def decrease_quantity(request, item_id):
    cart_item = get_object_or_404(
        CartItem, id=item_id, cart__user=request.user)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
        messages.success(
            request, f"Decreased quantity for {cart_item.session.title}.")
    else:
        cart_item.delete()
        messages.success(
            request, f"Removed {cart_item.session.title} from your cart.")
    return redirect('checkout:view_cart')


@login_required
@require_POST
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(
        CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(
        request, f"Removed {cart_item.session.title} from your cart.")
    return redirect('checkout:view_cart')


@login_required
def checkout(request):
    """A view that displays the checkout page."""
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY
    stripe.api_key = stripe_secret_key

    if not stripe_public_key:
        messages.warning(request, 'Stripe public key is missing.')
        return redirect('checkout:view_cart')

    try:
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('checkout:view_cart')

        total_price = cart.get_total_price()
        grand_total = total_price

        if request.method == 'POST':
            order_form = OrderForm(request.POST)
            if order_form.is_valid():
                order = order_form.save(commit=False)
                order.user = request.user
                order.order_number = uuid.uuid4().hex.upper()
                order.order_total = total_price
                order.grand_total = grand_total
                order.save()

                for cart_item in cart.items.all():
                    OrderLineItem.objects.create(
                        order=order,
                        session=cart_item.session,
                        quantity=cart_item.quantity,
                        price=cart_item.get_cost
                    )
                cart.items.all().delete()

                if 'payment_intent_id' in request.session:
                    del request.session['payment_intent_id']

                return redirect('checkout_success', order_number=order.order_number)
        else:
            order_form = OrderForm()

            try:
                intent = None
                if 'payment_intent_id' in request.session:
                    intent = stripe.PaymentIntent.retrieve(
                        request.session['payment_intent_id']
                    )
                    if intent.amount != int(grand_total * 100):
                        intent = stripe.PaymentIntent.modify(
                            intent.id,
                            amount=int(grand_total * 100)
                        )

                if not intent:
                    intent = stripe.PaymentIntent.create(
                        amount=int(grand_total * 100),
                        currency=settings.STRIPE_CURRENCY,
                        capture_method='automatic',
                        metadata={
                            'username': request.user.username,
                            'cart_items': ", ".join([
                                f"{item.session.title} (x{item.quantity})"
                                for item in cart.items.all()
                            ]),
                            'order_total': f"${grand_total:.2f}"
                        },
                        automatic_payment_methods={
                            'enabled': True,
                        },
                    )
                    request.session['payment_intent_id'] = intent.id
                    print("Client Secret:", intent.client_secret)

            except stripe.error.StripeError as e:
                messages.error(request, f'Payment processing error: {str(e)}')
                return redirect('checkout:view_cart')

            context = {
                'order_form': order_form,
                'stripe_public_key': stripe_public_key,
                'client_secret': intent.client_secret,
                'cart': cart,
                'total_price': total_price,
                'grand_total': grand_total,
            }
            return render(request, 'checkout/checkout.html', context)

    except Cart.DoesNotExist:
        messages.error(request, 'There was an error with your cart.')
        return redirect('checkout:view_cart')


def cart_total_view(user):
    """A view that calculates the total price of items in the user's cart."""
    cart = get_object_or_404(Cart, user=user)
    total = sum(item.get_cost *
                item.quantity for item in cart.items.all())
    return total


@login_required
@require_POST
def add_to_cart(request, session_id):
    try:
        session = Session.objects.get(id=session_id)

        if session.is_full():
            return JsonResponse({'success': False, 'error': 'Session is full'}, status=400)

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, session=session)

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        total = cart.get_total_price()

        return JsonResponse({'success': True, 'total': float(total)})
    except Session.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Session not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)


@login_required
def view_cart(request):
    """View to display the user's cart."""
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.select_related('session').all()
    total_items = cart_items.count()
    grand_total = cart.get_total_price()

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_items': total_items,
        'grand_total': grand_total,
    }
    return render(request, 'checkout/cart.html', context)


@csrf_exempt
def create_checkout_session(request):
    """A view that creates a checkout session with Stripe."""

    if os.environ.get('ENV') == 'PRODUCTION':
        YOUR_DOMAIN = "https://skill-sharing-446c0336ffb5.herokuapp.com"
    else:
        YOUR_DOMAIN = "http://localhost:8000"

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Session Name',
                    },
                    'unit_amount': 2000,
                },
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url=YOUR_DOMAIN + '/success/',
        cancel_url=YOUR_DOMAIN + '/cancel/',
    )

    return redirect(checkout_session.url, code=303)


def checkout_success(request, order_number):
    """Handle successful checkouts"""
    order = get_object_or_404(Order, order_number=order_number)

    if request.user.is_authenticated:
        profile = Profile.objects.get(user=request.user)
        order.user_profile = profile
        order.save()

    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
    }

    return render(request, template, context)


def payment_cancel(request):
    """A view that displays a cancellation message after payment is canceled."""
    return render(request, 'checkout/cancel.html')


@csrf_exempt
def cache_checkout_data(request):
    """A view that caches checkout data."""
    if request.method == 'POST':
        cart_data = request.POST.get('cart_data')
        user_info = request.POST.get('user_info')

        request.session['cart_data'] = cart_data
        request.session['user_info'] = user_info

        return JsonResponse({'status': 'success', 'message': 'Checkout data cached successfully.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


def calculate_cart_total(user):
    """A view that calculates the total price of items in the user's cart."""
    cart = get_object_or_404(Cart, user=user)
    total = sum(item.get_cost *
                item.quantity for item in cart.items.all())
    return total


def update_cart_quantity(request, item_id):
    """A view that updates the quantity of an item in the cart."""
    if request.method == 'POST':
        try:
            cart_item = get_object_or_404(
                CartItem, id=item_id, cart__user=request.user)
            quantity = int(request.POST.get('quantity', 1))

            if quantity > 0:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Cart updated successfully')
            else:
                cart_item.delete()
                messages.success(request, 'Item removed from cart')

            return JsonResponse({
                'success': True,
                'total': calculate_cart_total(request.user),
                'cart_count': cart_item.cart.items.count()
            })

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Invalid request method'})


def cart_contents_view(request):
    """View to display the contents of the user's cart."""
    cart_items = []
    total = 0
    item_count = 0

    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_items = cart.items.all()
            total = sum(item.get_cost *
                        item.quantity for item in cart_items)
            item_count = cart_items.count()
        except Cart.DoesNotExist:
            cart = None

    context = {
        'cart_items': cart_items,
        'total': total,
        'item_count': item_count,
    }

    return render(request, 'checkout/cart_contents.html', context)


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        # Handle different event types
        if event.type == 'payment_intent.succeeded':
            payment_intent = event.data.object
            handle_payment_success(payment_intent)
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@transaction.atomic
def process_order(order, cart):
    # Create order
    order.save()
    
    # Create line items
    for cart_item in cart.items.all():
        OrderLineItem.objects.create(
            order=order,
            session=cart_item.session,
            quantity=cart_item.quantity,
            price=cart_item.get_cost
        )
    
    # Clear cart
    cart.items.all().delete()


def check_session_availability(cart):
    for item in cart.items.all():
        if item.session.is_full():
            raise ValidationError(f"Session {item.session.title} is now full")


def handle_payment_success(payment_intent):
    # Get order using payment intent ID
    order = Order.objects.get(stripe_pid=payment_intent.id)
    order.payment_status = 'COMPLETED'
    order.save()

   
def create_payment_intent(amount, currency='usd'):
    payment_intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
    )
    return payment_intent.client_secret