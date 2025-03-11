from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Profile


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("A user with this email already exists.")
        return email


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'bio', 'skills', 'goals', 'experience', 'achievements',
            'profile_picture', 'linkedin_profile', 'github_profile',
            'mentorship_areas', 'availability', 'preferred_mentoring_method',
            'is_available'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'goals': forms.Textarea(attrs={'rows': 3}),
            'experience': forms.Textarea(attrs={'rows': 3}),
            'achievements': forms.Textarea(attrs={'rows': 3}),
            'mentorship_areas': forms.Textarea(attrs={'rows': 2}),
            'availability': forms.TextInput(attrs={'placeholder': 'e.g., Mon-Fri 9am-5pm'}),
        }

    def clean_linkedin_profile(self):
        linkedin_profile = self.cleaned_data.get('linkedin_profile')
        if linkedin_profile and not linkedin_profile.startswith('https://www.linkedin.com/in/'):
            raise ValidationError("Please enter a valid LinkedIn profile URL.")
        return linkedin_profile

    def clean_github_profile(self):
        github_profile = self.cleaned_data.get('github_profile')
        if github_profile and not github_profile.startswith('https://github.com/'):
            raise ValidationError("Please enter a valid GitHub profile URL.")
        return github_profile

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
