from django import forms
from allauth.account.forms import SignupForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class CustomSignupForm(SignupForm):
    is_expert = forms.BooleanField(required=False, label="Are you a mentor?")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Sign Up'))

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        user.profile.is_expert = self.cleaned_data.get('is_expert')
        user.profile.save()
        return user
