from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Profile


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
            "mentor_since": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "mentorship_areas": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "availability": forms.TextInput(attrs={"class": "form-control"}),
            "preferred_mentoring_method": forms.TextInput(attrs={"class": "form-control"}),
        }