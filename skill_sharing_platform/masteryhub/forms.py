from django import forms
from allauth.account.forms import SignupForm


class CustomSignupForm(SignupForm):
    is_expert = forms.BooleanField(required=False, label="Are you a mentor?")

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.profile.is_expert = self.cleaned_data.get("is_expert")
        user.profile.save()
        return user
