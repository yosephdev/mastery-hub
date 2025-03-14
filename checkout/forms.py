from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
import re

from profiles.models import Profile
from masteryhub.models import Session
from .models import Order

User = get_user_model()


class OrderForm(forms.ModelForm):
    """Form for handling order information during checkout."""

    country = CountryField(blank_label="Country *").formfield(
        widget=CountrySelectWidget(attrs={
            "class": "border-black rounded-0 profile-form-input"
        })
    )

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

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        # Remove any non-digit characters except for the leading +
        cleaned_phone = re.sub(r'[^\d+]', '', phone_number)
        
        # Check if the phone number is valid
        if not re.match(r'^\+?[1-9]\d{8,14}$', cleaned_phone):
            raise ValidationError(
                'Please enter a valid phone number (9-15 digits)'
            )
        return cleaned_phone

    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode')
        # Remove any spaces or hyphens
        cleaned_postcode = re.sub(r'[\s-]', '', postcode)
        
        # Check if the postcode contains only digits
        if not cleaned_postcode.isdigit():
            raise ValidationError(
                'Postal code should contain only numbers'
            )
        
        # Check if the postcode is a valid format
        if not re.match(r'^\d{5}(\d{4})?$', cleaned_postcode):
            raise ValidationError(
                'Please enter a valid postal code (e.g., 12345 or 123456789)'
            )
        return cleaned_postcode

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "full_name": "Full Name",
            "email": "Email Address",
            "phone_number": "Phone Number (e.g., +1234567890)",
            "postcode": "Postal Code (e.g., 12345)",
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
            self.fields[field].widget.attrs["class"] = "stripe-style-input"
            self.fields[field].label = False


class SessionForm(forms.ModelForm):
    """Form for creating and editing sessions."""

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
            "description": forms.Textarea(
                attrs={"class": "form-control", "rows": 4}
            ),
        }

    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise ValidationError("Price must be greater than zero")
        return price

    def clean_max_participants(self):
        max_participants = self.cleaned_data.get('max_participants')
        if max_participants <= 0:
            raise ValidationError("Max participants must be greater than zero")
        return max_participants


class ProfileForm(forms.ModelForm):
    """Form for user profile information."""

    mentor_since = forms.DateField(
        widget=forms.SelectDateWidget(),
        required=False
    )

    class Meta:
        model = Profile
        fields = [
            'bio',
            'skills',
            'mentor_since',
            'mentorship_areas',
            'availability',
            'is_available'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'skills': forms.Textarea(attrs={'rows': 3}),
            'mentorship_areas': forms.Textarea(attrs={'rows': 2}),
            'availability': forms.TextInput(attrs={'placeholder': 'e.g., Mon-Fri 9am-5pm'}),
        }

    def clean_mentor_since(self):
        mentor_since = self.cleaned_data.get('mentor_since')
        if mentor_since and mentor_since > timezone.now().date():
            raise ValidationError("Mentor since date cannot be in the future")
        return mentor_since

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
