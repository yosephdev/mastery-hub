from django import forms
from django.utils import timezone
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit
from django.core.validators import MinValueValidator, MaxValueValidator

from profiles.models import Profile
from masteryhub.models import (
    Session, Forum, ConcernReport, Booking,
    Review, MentorshipRequest
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
            "experience": forms.Textarea(
                attrs={"rows": 4, "class": "form-control"}
            ),
            "achievements": forms.Textarea(
                attrs={"rows": 4, "class": "form-control"}
            ),
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

    def clean_mentor_since(self):
        mentor_since = self.cleaned_data.get('mentor_since')
        if mentor_since and mentor_since > timezone.now().date():
            raise forms.ValidationError(
                "Mentor since date cannot be in the future")
        return mentor_since


class ForumPostForm(forms.ModelForm):
    class Meta:
        model = Forum
        fields = ["title", "content", "category"]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "content": forms.Textarea(
                attrs={"class": "form-control", "rows": 5}
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
        }


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
            "description": forms.Textarea(
                attrs={"rows": 5, "class": "form-control"}
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
        }


class OrderForm(forms.Form):
    full_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(max_length=254, required=True)
    address = forms.CharField(max_length=255, required=True)
    city = forms.CharField(max_length=50, required=True)
    postcode = forms.CharField(max_length=20, required=True)
    country = forms.CharField(max_length=50, required=True)

    def clean_postcode(self):
        postcode = self.cleaned_data.get('postcode')
        if not postcode.isdigit():
            raise forms.ValidationError(
                "Postal code must contain only numbers")
        return postcode


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['skill', 'scheduled_time', 'status']
        widgets = {
            'scheduled_time': forms.DateTimeInput(
                attrs={
                    'type': 'datetime-local',
                    'class': 'form-control'
                }
            ),
        }

    def clean_scheduled_time(self):
        scheduled_time = self.cleaned_data.get('scheduled_time')
        if scheduled_time and scheduled_time < timezone.now():
            raise forms.ValidationError("Scheduled time cannot be in the past")
        return scheduled_time


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(
                attrs={'class': 'form-control'},
                choices=[(i, str(i)) for i in range(1, 6)]
            ),
            'comment': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Write your review here...'
                }
            ),
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5")
        return rating


class MentorshipRequestForm(forms.ModelForm):
    class Meta:
        model = MentorshipRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Explain why you would like to be mentored...'
                }
            )
        }

    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message.strip()) < 50:
            raise forms.ValidationError(
                "Please provide a detailed message (at least 50 characters)"
            )
        return message
