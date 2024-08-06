from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit, Div
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import SignupForm as AllAuthSignupForm

from accounts.models import Profile
from masteryhub.models import Session, Forum, ConcernReport

User = get_user_model()


class CustomSignupForm(AllAuthSignupForm):
    username = forms.CharField(
        max_length=150,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.",
    )
    email = forms.EmailField()
    password1 = forms.CharField(
        widget=forms.PasswordInput,
        help_text=(
            "Your password can’t be too similar to your other personal information. "
            "Your password must contain at least 8 characters. "
            "Your password can’t be a commonly used password. "
            "Your password can’t be entirely numeric."
        ),
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput,
        help_text="Enter the same password as before, for verification.",
    )
    is_expert = forms.BooleanField(required=False)
    terms = forms.BooleanField(required=True)

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
                Div(Field("terms", id="id_terms_checkbox"), css_class="form-check"),
                css_class="form-group",
            ),
            Div(
                Submit("submit", "Sign Up", css_class="btn btn-primary"),
                css_class="d-flex justify-content-between align-items-center mt-4",
            ),
        )
        for field_name, field in self.fields.items():
            field.help_text = field.help_text.replace("<br>", " ")


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
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            "bio",
            "skills",
            "experience",
            "achievements",
            "profile_picture",
            "linkedin_profile",
            "github_profile",
            "is_expert",
            "mentor_since",
            "mentorship_areas",
            "availability",
            "preferred_mentoring_method",
        ]
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "skills": forms.TextInput(
                attrs={
                    "placeholder": "Enter skills separated by commas",
                    "class": "form-control",
                }
            ),
            "experience": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "achievements": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "mentor_since": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "mentorship_areas": forms.Textarea(
                attrs={"rows": 3, "class": "form-control"}
            ),
            "availability": forms.TextInput(attrs={"class": "form-control"}),
            "preferred_mentoring_method": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }


class ForumPostForm(forms.ModelForm):
    class Meta:
        model = Forum
        fields = ["title", "content", "category"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
            "category": forms.Select(attrs={"class": "form-control"}),
        }


class MentorApplicationForm(forms.Form):
    name = forms.CharField(
        label="Your Name",
        max_length=100,
        widget=forms.TextInput(
            attrs={"placeholder": "Enter your full name", "class": "form-control"}
        ),
    )
    email = forms.EmailField(
        label="Your Email",
        widget=forms.EmailInput(
            attrs={"placeholder": "Enter your email address", "class": "form-control"}
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
                Submit("submit", "Apply to be a Mentor", css_class="btn btn-primary")
            ),
        )


class ConcernReportForm(forms.ModelForm):
    class Meta:
        model = ConcernReport
        fields = ["category", "description"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5, "class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-control"}),
        }


class OrderForm(forms.Form):
    full_name = forms.CharField(max_length=50, required=True, label="Full Name")
    email = forms.EmailField(max_length=254, required=True, label="Email")
    street_address1 = forms.CharField(
        max_length=80, required=True, label="Street Address 1"
    )
    street_address2 = forms.CharField(
        max_length=80, required=False, label="Street Address 2"
    )
    county = forms.CharField(max_length=80, required=False, label="County")
    town_or_city = forms.CharField(max_length=80, required=True, label="Town/City")
    postcode = forms.CharField(max_length=20, required=True, label="Postcode")
    country = CountryField(blank_label="Country").formfield(
        widget=CountrySelectWidget(
            attrs={"class": "border-black rounded-0 profile-form-input"}
        )
    )
    phone_number = forms.CharField(max_length=20, required=True, label="Phone Number")

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

        # Setting autofocus for the 'full_name' field
        self.fields["full_name"].widget.attrs["autofocus"] = True
        # Adding placeholders and styles to form fields
        for field in self.fields:
            if field != "country":
                placeholder = placeholders.get(field, field)
                if self.fields[field].required:
                    placeholder += " *"
                self.fields[field].widget.attrs["placeholder"] = placeholder
            self.fields[field].widget.attrs["class"] = "stripe-style-input"
            self.fields[field].label = False
