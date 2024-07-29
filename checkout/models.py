from django.contrib.auth.models import User
from django.db import models
from masteryhub.models import Session

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='checkout_profile')
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=255, blank=True)
    goals = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True
    )
    linkedin_profile = models.URLField(blank=True)
    github_profile = models.URLField(blank=True)
    is_expert = models.BooleanField(default=False)
    mentor_since = models.DateField(null=True, blank=True)
    mentorship_areas = models.TextField(
        blank=True, help_text="Areas you're willing to mentor in, separated by commas"
    )
    availability = models.CharField(
        max_length=255, blank=True, help_text="Your general availability for mentoring"
    )
    preferred_mentoring_method = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., One-on-one, Group sessions, Online, In-person",
    )

    def __str__(self):
        return self.user.username

    class Meta:
        unique_together = ("user",)
        indexes = [models.Index(fields=["user"])]

class Payment(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(
        Session, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.user.username} - {self.amount} on {self.date}"

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_number = models.CharField(max_length=32, unique=True)
    date = models.DateTimeField(auto_now_add=True)
    full_name = models.CharField(max_length=50)
    street_address1 = models.CharField(max_length=80)
    street_address2 = models.CharField(max_length=80, blank=True)
    county = models.CharField(max_length=80, blank=True)
    town_or_city = models.CharField(max_length=80)
    postcode = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=40)
    phone_number = models.CharField(max_length=20)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.order_number