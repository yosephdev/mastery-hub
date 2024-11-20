from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit
from django.core.exceptions import ValidationError
import re
from django.utils import timezone

from profiles.models import Profile
from masteryhub.models import Session
from .models import Order

User = get_user_model()


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
