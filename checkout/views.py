from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit
from django.core.exceptions import ValidationError
import re
from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import stripe
from django.http import JsonResponse
import logging

from profiles.models import Profile
from masteryhub.models import Session
from .models import Order, CartItem, Cart

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
            raise ValidationError("The 'Mentor Since' date cannot be in the future.")
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
            'button_class': 'btn-outline-primary'
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
            'button_class': 'btn-black'
        }
    ]

    context = {
        'pricing_plans': pricing_plans
    }

    return render(request, 'checkout/pricing.html', context)


def increase_quantity(request, item_id):
    """A view that increases the quantity of an item in the cart."""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)  
        cart_item.quantity += 1  
        cart_item.save()  
        return redirect('view_cart')  


def decrease_quantity(request, item_id):
    """A view that decreases the quantity of an item in the cart."""
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)  
        if cart_item.quantity > 1:
            cart_item.quantity -= 1  
            cart_item.save()  
        else:
            cart_item.delete() 
        return redirect('view_cart') 


def remove_from_cart(request, item_id):
    """A view that removes an item from the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id)
    cart_item.delete()

    return redirect('view_cart')


def checkout(request):
    """A view that displays the checkout page."""
    if request.method == 'POST':
        order_form = OrderForm(request.POST)
        session_form = SessionForm(request.POST)

        if order_form.is_valid() and session_form.is_valid():            
            order = order_form.save()
            session = session_form.save(commit=False)
            session.order = order 
            session.save()
            return redirect('success')  
    else:
        order_form = OrderForm()
        session_form = SessionForm()
  
    cart = Cart.objects.get(user=request.user) 
    total_amount = int(cart.get_total_price() * 100)  
 
    order_id = f"ORDER-{timezone.now().strftime('%Y%m%d%H%M%S')}-{request.user.id}"

    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=total_amount,
            currency='usd',  
            automatic_payment_methods={'enabled': True},
            metadata={'order_id': order_id}
        )
        client_secret = payment_intent.client_secret
    except stripe.error.StripeError as e:       
        messages.error(request, f"An error occurred: {str(e)}")
        client_secret = None

    context = {
        'order_form': order_form,
        'session_form': session_form,
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
        'client_secret': client_secret,
        'order_id': order_id,  
    }

    return render(request, 'checkout/checkout.html', context)


def calculate_cart_total(user):
    """Calculate the total price of items in the user's cart."""
    cart = get_object_or_404(Cart, user=user)  
    total = sum(item.session.price * item.quantity for item in cart.items.all())
    return total

def add_to_cart(request, session_id):
    """A view that adds a session to the cart."""
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'error': 'User is not authenticated.'}, status=403)

        try:
            session = get_object_or_404(Session, id=session_id)
            
            cart, created = Cart.objects.get_or_create(user=request.user)           
          
            if created:
                logger.info(f"Created a new cart for user: {request.user.username}")

            cart_item, created = CartItem.objects.get_or_create(session=session, cart=cart)  
            cart_item.quantity += 1  
            cart_item.save()  
           
            logger.info(f"Added session '{session.title}' to cart for user: {request.user.username}. New quantity: {cart_item.quantity}")

            total = calculate_cart_total(request.user)  
            return JsonResponse({'success': True, 'total': total})

        except Exception as e:
            logger.error(f"Error adding to cart: {e}") 
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    return JsonResponse({'success': False, 'error': 'Invalid request method'}, status=400)


def view_cart(request):
    """View to display the user's cart."""
    if not request.user.is_authenticated:
        return redirect('login')  

    cart = get_object_or_404(Cart, user=request.user)  
    cart_items = cart.items.all()  
    total_items = cart_items.count()  
    total_price = sum(item.session.price * item.quantity for item in cart_items)  

    context = {
        'cart': cart,  
        'total_items': total_items,
        'grand_total': total_price,  
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


def checkout_success(request):
    """A view that displays a success message after checkout."""
    return render(request, 'checkout/checkout_success.html')  


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
    """Calculate the total price of items in the user's cart."""
    cart = get_object_or_404(Cart, user=user)  
    total = sum(item.session.price * item.quantity for item in cart.items.all())
    return total
