from django import forms
from django.contrib.auth.models import User
from .models import Profile

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

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
        }
