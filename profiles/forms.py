from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Profile


class ProfileForm(forms.ModelForm):
    MENTORING_METHODS = [
        ('one_on_one', 'One-on-One Sessions'),
        ('group', 'Group Sessions'),
        ('workshop', 'Workshops'),
        ('online', 'Online Sessions'),
        ('hybrid', 'Hybrid (Online & In-person)'),
        ('project', 'Project-based Mentoring')
    ]

    AVAILABILITY_CHOICES = [
        ('weekdays', 'Weekdays'),
        ('weekends', 'Weekends'),
        ('evenings', 'Evenings'),
        ('flexible', 'Flexible'),
        ('custom', 'Custom Schedule')
    ]

    class Meta:
        model = Profile
        fields = [
            "bio",
            "skills",
            "goals",
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
            "is_available"
        ]
        widgets = {
            "bio": forms.Textarea(attrs={
                "rows": 4,
                "class": "form-control",
                "placeholder": "Tell us about yourself..."
            }),
            "experience": forms.Textarea(attrs={
                "rows": 4,
                "class": "form-control",
                "placeholder": "Share your professional experience..."
            }),
            "achievements": forms.Textarea(attrs={
                "rows": 4,
                "class": "form-control",
                "placeholder": "List your key achievements..."
            }),
            "mentor_since": forms.DateInput(attrs={
                "type": "date",
                "class": "form-control"
            }),
            "mentorship_areas": forms.Textarea(attrs={
                "rows": 3,
                "class": "form-control",
                "placeholder": "Areas you can mentor in..."
            }),
            "linkedin_profile": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://linkedin.com/in/yourprofile"
            }),
            "github_profile": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://github.com/yourusername"
            }),
        }

    def clean_profile_picture(self):
        picture = self.cleaned_data.get('profile_picture')
        if picture:
            if picture.size > 5242880:
                raise forms.ValidationError(
                    _('Image file too large ( > 5MB )'))
            return picture
        return None

    def clean_linkedin_profile(self):
        url = self.cleaned_data.get('linkedin_profile')
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            if 'linkedin.com' not in url:
                raise forms.ValidationError(
                    _('Please enter a valid LinkedIn URL'))
        return url

    def clean_github_profile(self):
        url = self.cleaned_data.get('github_profile')
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            if 'github.com' not in url:
                raise forms.ValidationError(
                    _('Please enter a valid GitHub URL'))
        return url

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].required = False
            if isinstance(self.fields[field].widget, forms.TextInput) or \
               isinstance(self.fields[field].widget, forms.Textarea):
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })
