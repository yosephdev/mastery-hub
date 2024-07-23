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
        widget=forms.TextInput(attrs={"placeholder": "Enter your full name", "class": "form-control"}),
    )
    email = forms.EmailField(
        label="Your Email",
        widget=forms.EmailInput(attrs={"placeholder": "Enter your email address", "class": "form-control"}),
    )
    areas_of_expertise = forms.CharField(
        label="Areas of Expertise",
        widget=forms.Textarea(attrs={"placeholder": "Describe your areas of expertise", "class": "form-control", "rows": 4}),
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
