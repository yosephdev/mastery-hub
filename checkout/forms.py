from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit

from .models import Profile, Session

User = get_user_model()

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

class OrderForm(forms.Form):
    full_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(max_length=254, required=True)
    address = forms.CharField(max_length=255, required=True)
    city = forms.CharField(max_length=50, required=True)
    postcode = forms.CharField(max_length=20, required=True)
    country = forms.CharField(max_length=50, required=True)