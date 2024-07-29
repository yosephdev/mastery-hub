from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit

from .models import Profile, Session, Forum, ConcernReport

User = get_user_model()

class CustomSignupForm(UserCreationForm):
    is_expert = forms.BooleanField(required=False, label="Are you a mentor?")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Sign Up"))

    def save(self, request):
        user = super().save(request)
        profile, created = Profile.objects.get_or_create(user=user)
        profile.is_expert = self.cleaned_data.get("is_expert")
        profile.save()
        return user

    def signup(self, request, user):
        profile, created = Profile.objects.get_or_create(user=user)
        profile.is_expert = self.cleaned_data.get("is_expert")
        profile.save()
        return user

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
            "date": forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}),
            "duration": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
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
            "skills": forms.TextInput(attrs={"placeholder": "Enter skills separated by commas", "class": "form-control"}),
            "experience": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "achievements": forms.Textarea(attrs={"rows": 4, "class": "form-control"}),
            "mentor_since": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "mentorship_areas": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "availability": forms.TextInput(attrs={"class": "form-control"}),
            "preferred_mentoring_method": forms.TextInput(attrs={"class": "form-control"}),
        }

class OrderForm(forms.Form):
    full_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(max_length=254, required=True)
    address = forms.CharField(max_length=255, required=True)
    city = forms.CharField(max_length=50, required=True)
    postcode = forms.CharField(max_length=20, required=True)
    country = forms.CharField(max_length=50, required=True)