import uuid
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.db import models
from masteryhub.models import Session
from profiles.models import Profile
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class Payment(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(
        Session, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.user.username} - {self.amount} on {self.date}"


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_active']),
        ]

    def get_total_price(self):
        """Calculate total price with any applicable discounts."""
        total = sum(item.get_cost() for item in self.items.all())
        if self.is_eligible_for_discount():
            total = self.apply_discount(total)
        return Decimal(total).quantize(Decimal('0.00'))

    def is_eligible_for_discount(self):
        """Check if cart is eligible for any discounts."""
        total_items = self.items.count()
        total_price = sum(item.get_cost() for item in self.items.all())

        return total_items >= 3 or total_price >= Decimal('100.00')

    def apply_discount(self, total):
        """Apply discount rules to the total."""
        if total >= Decimal('100.00'):
            return total * Decimal('0.90')
        return total

    def clear(self):
        """Clear all items from cart."""
        self.items.all().delete()
        self.save()

    def validate_cart_items(self):
        """Validate all items in cart are still available."""
        for item in self.items.all():
            if item.session.is_full():
                raise ValidationError(
                    f"Session '{item.session.title}' is now full")
            if not item.session.is_active:
                raise ValidationError(
                    f"Session '{item.session.title}' is no longer available")

    def mark_inactive(self):
        """Mark cart as inactive (e.g., after checkout)."""
        self.is_active = False
        self.save()

    def __str__(self):
        return f"Cart for {self.user.username} ({self.items.count()} items)"


class CartItem(models.Model):
    cart = models.ForeignKey(
        'Cart', related_name='items', on_delete=models.CASCADE)
    session = models.ForeignKey('masteryhub.Session', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price_at_time_of_adding = models.DecimalField(
        max_digits=10, decimal_places=2, null=True)

    class Meta:
        ordering = ['created_at']
        unique_together = ['cart', 'session']
        indexes = [
            models.Index(fields=['cart', 'session']),
        ]

    def clean(self):
        """Validate cart item."""
        if self.session.is_full():
            raise ValidationError("This session is full")
        if self.quantity > self.session.available_spots:
            raise ValidationError(
                f"Only {self.session.available_spots} spots available")

    def save(self, *args, **kwargs):
        """Override save to store current price and validate."""
        if not self.price_at_time_of_adding:
            self.price_at_time_of_adding = self.session.price
        self.clean()
        super().save(*args, **kwargs)

    def get_cost(self):
        """Calculate cost using the price at the time of adding"""
        try:
            return Decimal(str(self.price_at_time_of_adding * self.quantity))
        except (TypeError, ValueError) as e:
            logger.error(f"Error calculating cart item cost: {e}")
            return Decimal('0.00')

    def get_savings(self):
        """Calculate savings if current price is different."""
        current_price = self.session.price
        if current_price > self.price_at_time_of_adding:
            return Decimal((current_price - self.price_at_time_of_adding) * self.quantity).quantize(Decimal('0.00'))
        return Decimal('0.00')

    def __str__(self):
        return f"{self.quantity}x {self.session.title} in cart for {self.cart.user.username}"


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=32, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, blank=True, null=True)
    street_address1 = models.CharField(max_length=80)
    street_address2 = models.CharField(max_length=80, blank=True)
    county = models.CharField(max_length=80, blank=True)
    town_or_city = models.CharField(max_length=80)
    postcode = models.CharField(max_length=20, blank=True)
    country = CountryField(blank_label="Country *", null=False, blank=False)
    phone_number = models.CharField(max_length=20)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_cost = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_pid = models.CharField(max_length=255, null=True, blank=True)
    confirmation_email_sent = models.BooleanField(default=False)

    def _generate_order_number(self):
        """Generate a random, unique order number using UUID"""
        return uuid.uuid4().hex.upper()

    def save(self, *args, **kwargs):
        """Override the original save method to set the order number if not set"""
        if not self.order_number:
            self.order_number = self._generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number


class OrderLineItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='lineitems')
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Session {self.title} - {self.date.strftime("%Y-%m-%d %H:%M")}'
