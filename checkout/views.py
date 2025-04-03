import re
import uuid
import logging
from functools import wraps
from decimal import Decimal

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.decorators.vary import vary_on_cookie
from django.template.loader import render_to_string

import stripe

from profiles.models import Profile
from profiles.forms import ProfileForm
from masteryhub.models import Session
from .models import Order, CartItem, Cart, OrderLineItem
from .decorators import cart_action_handler


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


def cart_action_handler(action_type):
    """Decorator for cart actions with error handling and logging."""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            try:
                with transaction.atomic():
                    result = view_func(request, *args, **kwargs)
                    logger.info(
                        f"Cart {action_type} successful for user {request.user.id}")
                    return result
            except ValidationError as e:
                logger.warning(
                    f"Cart {action_type} validation error for user {request.user.id}: {str(e)}")
                messages.error(request, str(e))
            except Exception as e:
                logger.error(
                    f"Cart {action_type} error for user {request.user.id}: {str(e)}")
                messages.error(
                    request, "An unexpected error occurred. Please try again.")
            return redirect('checkout:view_cart')
        return _wrapped_view
    return decorator


@login_required
@cart_action_handler("add")
@require_POST
def add_to_cart(request, session_id):
    try:
        session = Session.objects.get(id=session_id)

        if request.user.profile in session.participants.all():
            messages.error(
                request, 'You are already enrolled in this session!')
            return JsonResponse({
                'success': False,
                'error': 'Already enrolled'
            })

        if session.is_full():
            messages.error(request, 'This session is full!')
            return JsonResponse({
                'success': False,
                'error': 'Session is full'
            })

        cart, _ = Cart.objects.get_or_create(user=request.user)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            session=session,
            defaults={
                'quantity': 1,
                'price_at_time_of_adding': session.price
            }
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        total = cart.get_total_price()

        messages.success(
            request,
            f'Added {session.title} to your cart!'
        )

        return JsonResponse({
            'success': True,
            'total': float(total)
        })

    except Session.DoesNotExist:
        messages.error(request, 'Session not found!')
        return JsonResponse({
            'success': False,
            'error': 'Session not found'
        }, status=404)
    except Exception as e:
        messages.error(request, f'Error adding session to cart: {str(e)}')
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@cache_page(60 * 5)
@vary_on_cookie
def pricing(request):
    """Cached view for pricing information."""
    pricing_plans = cache.get('pricing_plans')
    if pricing_plans is None:
        pricing_plans = [
            {
                'name': 'Basic',
                'price': Decimal('9.99'),
                'features': [
                    'Access to 5 sessions per month',
                    'Basic mentorship features',
                    'Email support'
                ],
                'button_class': 'btn-outline-dark'
            },
            {
                'name': 'Pro',
                'price': Decimal('19.99'),
                'features': [
                    'Access to 15 sessions per month',
                    'Advanced mentorship features',
                    'Priority email support'
                ],
                'button_class': 'btn-success'
            },
            {
                'name': 'Enterprise',
                'price': Decimal('49.99'),
                'features': [
                    'Unlimited access to sessions',
                    'Premium mentorship features',
                    '24/7 phone and email support'
                ],
                'button_class': 'btn-info'
            }
        ]
        cache.set('pricing_plans', pricing_plans, 60 * 60)

    context = {
        'pricing_plans': pricing_plans,
        'is_authenticated': request.user.is_authenticated
    }
    return render(request, 'checkout/pricing.html', context)


@login_required
def view_cart(request):
    print("Template path:", request.resolver_match.view_name)
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_items': cart_items.count(),
        'grand_total': cart.get_total_price(),
    }

    response = render(request, 'checkout/cart.html', context)

    print("Rendered HTML:")
    print(response.content.decode())

    print("Response status:", response.status_code)
    return response


def create_order(user, order_form, cart, grand_total):
    """Create a new order from form data and cart."""
    order = order_form.save(commit=False)
    order.user = user
    order.order_number = uuid.uuid4().hex.upper()
    order.order_total = grand_total
    order.grand_total = grand_total
    order.stripe_pid = cart.stripe_pid if hasattr(cart, 'stripe_pid') else None
    order.save()

    return order


@login_required
@transaction.atomic
def checkout(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            messages.error(request, 'Your cart is empty.')
            return redirect('checkout:view_cart')
        cart.validate_cart_items()
        total_price = cart.get_total_price()
        grand_total = total_price
        stripe_total = int(grand_total * 100)

        if request.method == 'POST':
            order_form = OrderForm(request.POST)
            if order_form.is_valid():
                try:
                    # Create payment intent first
                    intent = stripe.PaymentIntent.create(
                        amount=stripe_total,
                        currency=settings.STRIPE_CURRENCY,
                        metadata={
                            'user_id': request.user.id,
                            'username': request.user.username,
                            'cart_id': cart.id
                        },
                        automatic_payment_methods={
                            'enabled': True,
                        }
                    )
                    # Assign stripe_pid to the cart
                    cart.stripe_pid = intent.id
                    cart.save()

                    # Create the order with the payment intent ID
                    order = order_form.save(commit=False)
                    order.user = request.user
                    order.email = order_form.cleaned_data['email']
                    order.order_total = grand_total
                    order.grand_total = grand_total
                    order.stripe_pid = intent.id
                    order.save()

                    # Create order line items
                    for cart_item in cart.items.all():
                        OrderLineItem.objects.create(
                            order=order,
                            session=cart_item.session,
                            quantity=cart_item.quantity,
                            price=cart_item.get_cost()
                        )
                    
                    # Clear the cart
                    cart.items.all().delete()
                    cart.delete()

                    # Send confirmation email
                    try:
                        subject = f'Order Confirmation - {order.order_number}'
                        context = {
                            'order': order,
                            'contact_email': settings.DEFAULT_FROM_EMAIL
                        }

                        # Plain text email
                        message = render_to_string(
                            'checkout/confirmation_emails/confirmation_email_body.txt',
                            context
                        )

                        # HTML email
                        html_message = render_to_string(
                            'checkout/confirmation_emails/confirmation_email.html',
                            context
                        )

                        # Send to both user and admin
                        recipient_list = [order.email]
                        if settings.DEFAULT_FROM_EMAIL:
                            recipient_list.append(settings.DEFAULT_FROM_EMAIL)

                        send_mail(
                            subject,
                            message,
                            settings.DEFAULT_FROM_EMAIL,
                            recipient_list,
                            fail_silently=False,
                            html_message=html_message
                        )

                        order.confirmation_email_sent = True
                        order.save()
                        messages.success(
                            request, "A confirmation email has been sent to your inbox.")
                    except Exception as e:
                        error_message = f"Error sending confirmation email: {str(e)}"
                        logger.error(error_message)
                        messages.error(request, error_message)

                    return redirect('checkout:checkout_success', order_number=order.order_number)
                except stripe.error.StripeError as e:
                    messages.error(
                        request, f'Error creating payment intent: {str(e)}')
                    if 'order' in locals():
                        order.lineitems.all().delete()
                        order.delete()
                    return redirect('checkout:view_cart')
            else:
                messages.error(
                    request, 'Please correct the errors in the form.')
        else:
            # Get user's profile data for pre-filling the form
            try:
                profile = request.user.profile
                initial_data = {
                    'full_name': request.user.get_full_name(),
                    'email': request.user.email,
                    'phone_number': profile.phone_number if profile.phone_number else ''
                }
            except Profile.DoesNotExist:
                initial_data = {
                    'full_name': request.user.get_full_name(),
                    'email': request.user.email
                }
            order_form = OrderForm(initial=initial_data)
            # Create payment intent for the form
            try:
                intent = stripe.PaymentIntent.create(
                    amount=stripe_total,
                    currency=settings.STRIPE_CURRENCY,
                    metadata={
                        'user_id': request.user.id,
                        'username': request.user.username,
                        'cart_id': cart.id
                    },
                    automatic_payment_methods={
                        'enabled': True,
                    }
                )
                client_secret = intent.client_secret
            except stripe.error.StripeError as e:
                messages.error(
                    request, f'Error creating payment intent: {str(e)}')
                return redirect('checkout:view_cart')
        context = {
            'order_form': order_form,
            'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
            'client_secret': client_secret if 'client_secret' in locals() else None,
            'cart': cart,
            'total_price': total_price,
            'grand_total': grand_total,
        }
        return render(request, 'checkout/checkout.html', context)
    except Cart.DoesNotExist:
        messages.error(request, 'Your cart is empty.')
        return redirect('checkout:view_cart')


def cart_total_view(user):
    """A view that calculates the total price of items in the user's cart."""
    cart = get_object_or_404(Cart, user=user)
    total = sum(item.get_cost() *
                item.quantity for item in cart.items.all())
    return total


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


def checkout_success(request, order_number):
    """
    Handle successful checkouts.
    """
    order = get_object_or_404(Order, order_number=order_number)
    save_info = request.session.get('save_info', False)

    if request.user.is_authenticated:
        try:
            profile = Profile.objects.get(user=request.user)
            order.user_profile = profile
            order.save()

            if save_info:
                profile_data = {
                    'default_phone_number': order.phone_number,
                    'default_country': order.country,
                    'default_postcode': order.postcode,
                    'default_town_or_city': order.town_or_city,
                    'default_street_address1': order.street_address1,
                    'default_street_address2': order.street_address2,
                    'default_county': order.county,
                }
                profile_form = ProfileForm(profile_data, instance=profile)
                if profile_form.is_valid():
                    profile_form.save()
                    messages.success(
                        request, "Your profile has been updated with your order details.")
                else:
                    messages.warning(
                        request, "Failed to update your profile. Please check your information.")

        except Profile.DoesNotExist:
            messages.error(
                request, "Profile not found. Unable to link order to your account.")
            return redirect('home')

    if 'cart' in request.session:
        del request.session['cart']

    # Step 1: Check if the email exists before sending
    if not order.email:
        messages.error(request, "No email address found for this order.")
        return redirect('home')

    # Step 2: Temporarily remove the check for confirmation_email_sent
    try:
        subject = f'MasteryHub - Order Confirmation #{order.order_number}'
        context = {
            'order': order,
            'contact_email': settings.DEFAULT_FROM_EMAIL,
            'site_name': 'MasteryHub',
        }

        # Plain text email
        message = render_to_string(
            'checkout/confirmation_emails/confirmation_email_body.txt',
            context
        )

        # HTML email
        html_message = render_to_string(
            'checkout/confirmation_emails/confirmation_email.html',
            context
        )

        # Send to both user and admin
        recipient_list = [order.email]
        if settings.DEFAULT_FROM_EMAIL:
            recipient_list.append(settings.DEFAULT_FROM_EMAIL)

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
            html_message=html_message
        )

        order.confirmation_email_sent = True
        order.save()       

    except Exception as e:
        error_message = f"Error sending confirmation email: {str(e)}"
        logger.error(error_message)
        messages.error(request, error_message)

    template = 'checkout/checkout_success.html'
    context = {
        'order': order,
        'from_profile': False,
    }

    return render(request, template, context)


def payment_cancel(request):
    """A view that displays a cancellation message after payment is canceled."""
    messages.error(request, "Payment was canceled. Please try again.")
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
            total = sum(item.get_cost() *
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


@transaction.atomic
def process_order(order, cart):
    order.save()

    for cart_item in cart.items.all():
        OrderLineItem.objects.create(
            order=order,
            session=cart_item.session,
            quantity=cart_item.quantity,
            price=cart_item.get_cost()
        )

    cart.items.all().delete()


def check_session_availability(cart):
    for item in cart.items.all():
        if item.session.is_full():
            raise ValidationError(f"Session {item.session.title} is now full")


def handle_payment_success(payment_intent):
    """Handle successful payment event from Stripe."""
    try:
        order = Order.objects.get(stripe_pid=payment_intent.id)
        if order.payment_status != 'COMPLETED':
            order.payment_status = 'COMPLETED'
            order.status = 'completed'
            order.save()

            if not order.confirmation_email_sent:
                try:
                    subject = f'MasteryHub - Order Confirmation #{order.order_number}'
                    context = {
                        'order': order,
                        'contact_email': settings.DEFAULT_FROM_EMAIL,
                        'site_name': 'MasteryHub',
                    }

                    # Plain text email
                    message = render_to_string(
                        'checkout/confirmation_emails/confirmation_email_body.txt',
                        context
                    )

                    # HTML email
                    html_message = render_to_string(
                        'checkout/confirmation_emails/confirmation_email.html',
                        context
                    )

                    # Send to both user and admin
                    recipient_list = [order.email]
                    if settings.DEFAULT_FROM_EMAIL:
                        recipient_list.append(settings.DEFAULT_FROM_EMAIL)

                    send_mail(
                        subject,
                        message,
                        settings.DEFAULT_FROM_EMAIL,
                        recipient_list,
                        fail_silently=False,
                        html_message=html_message
                    )

                    order.confirmation_email_sent = True
                    order.save()
                    logger.info(
                        f"Order {order.order_number} marked as completed and confirmation email sent.")
                except Exception as e:
                    logger.error(
                        f"Error sending confirmation email for order {order.order_number}: {str(e)}")
    except Order.DoesNotExist:
        logger.error(f"Order not found for PaymentIntent {payment_intent.id}")
        raise Exception("Order not found")


def handle_charge_success(charge):
    """Handle successful charge event from Stripe."""
    logger.info(f"Charge {charge.id} succeeded.")
    logger.info(f"Payment succeeded for Charge {charge.id}")


def handle_dispute_created(dispute):
    """Handle dispute created event from Stripe."""
    logger.warning(f"Dispute created for Charge {dispute.charge}")


def create_payment_intent(amount, currency='usd'):
    payment_intent = stripe.PaymentIntent.create(
        amount=amount,
        currency=currency,
    )
    return payment_intent.client_secret


def handle_payment_failure(payment_intent):
    """Handle payment failure event from Stripe."""
    try:
        order = Order.objects.filter(stripe_pid=payment_intent.id).first()
        if order:
            order.payment_status = 'FAILED'
            order.save()

            try:
                subject = f'MasteryHub - Payment Failed for Order #{order.order_number}'
                context = {
                    'order': order,
                    'contact_email': settings.DEFAULT_FROM_EMAIL,
                    'site_name': 'MasteryHub',
                }

                # Plain text email
                message = render_to_string(
                    'checkout/confirmation_emails/payment_failure_email.txt',
                    context
                )

                # HTML email
                html_message = render_to_string(
                    'checkout/confirmation_emails/payment_failure_email.html',
                    context
                )

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [order.email],
                    fail_silently=False,
                    html_message=html_message
                )

                logger.info(
                    f"Payment failure email sent for order {order.order_number}")
            except Exception as e:
                logger.error(
                    f"Error sending payment failure email for order {order.order_number}: {str(e)}")

            logger.warning(f"Order {order.order_number} marked as failed.")
    except Exception as e:
        logger.error(f"Error handling payment failure: {str(e)}")


@login_required
@csrf_exempt
def create_checkout_session(request):
    """Create a Stripe Checkout Session for payment processing."""
    try:
        cart = Cart.objects.get(user=request.user)
        if not cart.items.exists():
            return JsonResponse({'error': 'Cart is empty'}, status=400)

        domain = "https://skill-sharing-446c0336ffb5.herokuapp.com"

        for item in cart.items.all():
            if item.session.is_full():
                return JsonResponse({
                    'error': f'Session "{item.session.title}" is now full'
                }, status=400)

            if not item.session.is_active:
                return JsonResponse({
                    'error': f'Session "{item.session.title}" is no longer available'
                }, status=400)

        line_items = []
        total_amount = 0

        for item in cart.items.all():
            price = int(item.session.price * 100)
            if price <= 0:
                return JsonResponse({
                    'error': f'Invalid price for session "{item.session.title}"'
                }, status=400)

            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'unit_amount': price,
                    'product_data': {
                        'name': item.session.title,
                        'description': item.session.description[:255],
                    },
                },
                'quantity': item.quantity,
            })
            total_amount += price * item.quantity

        checkout_session = stripe.checkout.Session.create(
            customer_email=request.user.email,
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f"{domain}/checkout/success/",
            cancel_url=f"{domain}/checkout/cancel/",
            metadata={
                'user_id': request.user.id,
                'cart_id': cart.id,
                'total_amount': total_amount,
            }
        )

        return JsonResponse({'sessionId': checkout_session.id})

    except Cart.DoesNotExist:
        return JsonResponse({'error': 'Cart not found'}, status=404)
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {str(e)}")
        return JsonResponse({'error': 'Payment processing error'}, status=400)
    except Exception as e:
        logger.error(f"Checkout error: {str(e)}")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)


def handle_payment_intent(request, amount):
    """Create or retrieve Stripe PaymentIntent"""
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        amount_cents = int(Decimal(str(amount)) * 100)

        intent = stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=settings.STRIPE_CURRENCY,
            metadata={
                'user_id': request.user.id,
                'username': request.user.username,
            },
            automatic_payment_methods={'enabled': True},
        )
        return intent
    except (TypeError, ValueError) as e:
        logger.error(f"Error converting amount to cents: {e}")
        raise ValidationError("Invalid amount for payment")
    except stripe.error.StripeError as e:
        logger.error(f"Stripe PaymentIntent error: {str(e)}")
        raise
