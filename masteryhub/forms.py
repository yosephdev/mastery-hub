from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

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
        user = super().save(commit=False)
        user.save()
        user.profile.is_expert = self.cleaned_data.get("is_expert")
        user.profile.save()
        return user

    def signup(self, request, user):
        user.profile.is_expert = self.cleaned_data.get("is_expert")
        user.profile.save()


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Update Profile"))
