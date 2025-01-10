from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.contrib.auth.forms import UserChangeForm, SetPasswordForm
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit, Div
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm as AllAuthSignupForm
from allauth.account.forms import LoginForm as AllAuthLoginForm
from allauth.account.forms import ResetPasswordForm
from django.utils import timezone
import re

from profiles.models import Profile
from masteryhub.models import Session, ConcernReport

User = get_user_model()


class CustomLoginForm(AllAuthLoginForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Field("login", css_class="form-control"),
                Field("password", css_class="form-control"),
                Div(
                    Field("remember", css_class="form-check-input"),
                    css_class="form-check"
                ),
                css_class="form-group"
            ),
            Div(
                Submit("submit", "Sign In", css_class="btn btn-primary"),
                css_class="d-flex justify-content-between align-items-center mt-4",
            ),
        )
        self.fields["login"].widget.attrs.update({
            "placeholder": "Username or Email",
            "class": "form-control"
        })
        self.fields["password"].widget.attrs.update({
            "placeholder": "Password",
            "class": "form-control"
        })
        if "remember" in self.fields:
            self.fields["remember"].widget.attrs.update({
                "class": "form-check-input"
            })


class CustomSignupForm(AllAuthSignupForm):
    username = forms.CharField(
        max_length=150,
        help_text=(
            "Required. 150 characters or fewer. "
            "Letters, digits, and @/./+/-/_ only."
        ),
    )
    email = forms.EmailField()
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        help_text=(
            "Your password can't be too similar to your personal information. "
            "Your password must contain at least 8 characters. "
            "Your password can't be a commonly used password. "
            "Your password can't be entirely numeric."
        ),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Enter the same password as before, for verification.",
    )
    is_expert = forms.BooleanField(required=False)
    terms = forms.BooleanField(
        required=True,
        error_messages={'required': 'You must accept the terms and conditions'}
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Div(
                Field("username"),
                Field("email"),
                Field("password1"),
                Field("password2"),
                Field("is_expert"),
                Div(
                    Field("terms", id="id_terms_checkbox"),
                    css_class="form-check"
                ),
                css_class="form-group",
            ),
            Div(
                Submit("submit", "Sign Up", css_class="btn btn-primary"),
                css_class="d-flex justify-content-between align-items-center mt-4",
            ),
        )
        for field_name, field in self.fields.items():
            field.help_text = field.help_text.replace("<br>", " ")

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("username", css_class="form-control"),
            Field("email", css_class="form-control"),
            Field("first_name", css_class="form-control"),
            Field("last_name", css_class="form-control"),
            ButtonHolder(
                Submit("submit", "Update Profile", css_class="btn btn-primary")
            ),
        )


class SessionForm(forms.ModelForm):
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
            raise forms.ValidationError("Price must be greater than zero")
        return price

    def clean_mentor_since(self):
        mentor_since = self.cleaned_data.get('mentor_since')
        if mentor_since and mentor_since > timezone.now().date():
            raise forms.ValidationError("The date cannot be in the future.")
        return mentor_since


class MentorApplicationForm(forms.Form):
    name = forms.CharField(
        label="Your Name",
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "placeholder": "Enter your full name",
                "class": "form-control"
            }
        ),
    )
    email = forms.EmailField(
        label="Your Email",
        widget=forms.EmailInput(
            attrs={
                "placeholder": "Enter your email address",
                "class": "form-control"
            }
        ),
    )
    areas_of_expertise = forms.CharField(
        label="Areas of Expertise",
        widget=forms.Textarea(
            attrs={
                "placeholder": "Describe your areas of expertise",
                "class": "form-control",
                "rows": 4,
            }
        ),
    )

    def __init__(self, *args, **kwargs):
        super(MentorApplicationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Field("name"),
            Field("email"),
            Field("areas_of_expertise"),
            ButtonHolder(
                Submit(
                    "submit", "Apply to be a Mentor",
                    css_class="btn btn-primary"
                )
            ),
        )


class ConcernReportForm(forms.ModelForm):
    class Meta:
        model = ConcernReport
        fields = ["category", "description"]
        widgets = {
            "description": forms.Textarea(attrs={
                "rows": 5,
                "class": "form-control"
            }),
            "category": forms.Select(attrs={"class": "form-control"}),
        }


class OrderForm(forms.Form):
    full_name = forms.CharField(
        max_length=50, required=True, label="Full Name")
    email = forms.EmailField(max_length=254, required=True, label="Email")
    street_address1 = forms.CharField(
        max_length=80, required=True, label="Street Address 1")
    street_address2 = forms.CharField(
        max_length=80, required=False, label="Street Address 2")
    county = forms.CharField(max_length=80, required=False, label="County")
    town_or_city = forms.CharField(
        max_length=80, required=True, label="Town/City")
    postcode = forms.CharField(max_length=20, required=True, label="Postcode")
    country = CountryField(blank_label="Country").formfield(
        widget=CountrySelectWidget(
            attrs={"class": "border-black rounded-0 profile-form-input"}
        )
    )
    phone_number = forms.CharField(
        max_length=20, required=True, label="Phone Number")

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if not re.match(r'^\+?1?\d{9,15}$', phone_number):
            raise forms.ValidationError(
                'Please enter a valid phone number (9-15 digits)'
            )
        return phone_number

    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode')
        if not re.match(r'^\d{5}(?:[-\s]\d{4})?$', postcode):
            raise forms.ValidationError(
                'Please enter a valid postal code (e.g., 12345 or 12345-6789)'
            )
        return postcode

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            "full_name": "Full Name",
            "email": "Email Address",
            "street_address1": "Street Address 1",
            "street_address2": "Street Address 2",
            "county": "County",
            "town_or_city": "Town/City",
            "postcode": "Postal Code",
            "phone_number": "Phone Number",
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


class CustomSetPasswordForm(SetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].widget.attrs.update({
            'placeholder': 'New Password',
            'class': 'form-control'
        })
        self.fields['new_password2'].widget.attrs.update({
            'placeholder': 'Confirm Password',
            'class': 'form-control'
        })


class CustomResetPasswordForm(ResetPasswordForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Div(
                Field('email', css_class='form-control'),
                css_class='form-group'
            ),
            Div(
                Submit('submit', 'Reset Password',
                       css_class='btn btn-primary'),
                css_class='d-flex justify-content-between align-items-center mt-4',
            )
        )
        self.fields['email'].widget.attrs.update({
            'placeholder': 'Email Address',
            'class': 'form-control'
        })
