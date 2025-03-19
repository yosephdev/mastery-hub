from django.http import HttpResponseRedirect, Http404
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView,
    PasswordResetDoneView, PasswordResetConfirmView,
    PasswordResetCompleteView
)
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from allauth.account.views import ConfirmEmailView, SignupView
from allauth.account.models import EmailConfirmationHMAC, EmailAddress
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from accounts.forms import CustomSetPasswordForm
import logging
from allauth.socialaccount.views import LoginCancelledView
from allauth.socialaccount.models import SocialLogin, SocialAccount
from django.views.generic import RedirectView, View
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from profiles.models import Profile
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from allauth.socialaccount.providers.oauth2.client import OAuth2Client

from .forms import (
    CustomSignupForm,
    CustomSetPasswordForm,
)

logger = logging.getLogger(__name__)


@method_decorator(sensitive_post_parameters(), name='dispatch')
@method_decorator(csrf_protect, name='dispatch')
@method_decorator(never_cache, name='dispatch')
class CustomSignupView(SignupView):
    form_class = CustomSignupForm
    template_name = 'account/signup.html'
    success_url = reverse_lazy('home:index')

    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            if self.user:
                login(self.request, self.user)
                messages.success(self.request, 'Account created successfully!')
            return response
        except Exception as e:
            messages.error(self.request, f'An error occurred during signup: {str(e)}')
            return self.form_invalid(form)

signup_view = CustomSignupView.as_view()


class CustomConfirmEmailView(ConfirmEmailView):
    template_name = "account/email_confirm.html"

    def get_object(self, _=None):
        key = self.kwargs.get("key")
        if not key:
            raise Http404("No key provided")
        email_confirmation = EmailConfirmationHMAC.from_key(key)
        if email_confirmation is None:
            raise Http404("Invalid key")
        return email_confirmation

    def dispatch(self, request, *args, **kwargs):
        try:
            email_confirmation = self.get_object()
            if email_confirmation.key_expired():
                messages.error(
                    request, "The confirmation link has expired. Please request a new one.")
                return redirect("accounts:login")
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            messages.error(
                request, "Invalid confirmation link. Please request a new one.")
            return redirect("accounts:login")

    def get(self, request, *args, **kwargs):
        try:
            email_confirmation = self.get_object()
            email_confirmation.confirm(request)
            messages.success(
                request, "Your email has been confirmed successfully! You can now fully access all features of MasteryHub.")
            return redirect("accounts:login")
        except Exception as e:
            logger.error(f"Email confirmation error: {str(e)}")
            messages.error(
                request, "There was an error confirming your email. Please try again or contact support.")
            return redirect("accounts:login")


def send_confirmation_email(user, request):
    current_site = get_current_site(request)
    subject = 'Confirm Your MasteryHub Email Address'

    email_address, created = EmailAddress.objects.get_or_create(
        user=user,
        email=user.email,
        defaults={'verified': False, 'primary': True}
    )

    email_confirmation = EmailConfirmationHMAC(email_address)

    protocol = 'https' if request.is_secure() else 'http'
    activate_url = f"{protocol}://{current_site.domain}/accounts/confirm-email/{email_confirmation.key}/"

    current_site.name = "MasteryHub"

    message = render_to_string('account/email/email_confirmation_message.html', {
        'user': user,
        'current_site': current_site,
        'domain': current_site.domain,
        'activate_url': activate_url,
        'expiry_days': 3,
        'site_name': "MasteryHub"
    })

    text_message = render_to_string('account/email/email_confirmation_message.txt', {
        'user': user,
        'current_site': current_site,
        'domain': current_site.domain,
        'activate_url': activate_url,
        'site_name': "MasteryHub"
    })

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_message,
        from_email='noreply@masteryhub.com',
        to=[user.email]
    )
    email.attach_alternative(message, "text/html")
    email.send()


class CustomLoginView(LoginView):
    """Handle user login."""
    template_name = "account/login.html"

    def form_valid(self, form):
        storage = messages.get_messages(self.request)
        storage.used = True

        user = form.get_user()
        auth_login(self.request, user)
        if not self.request.session.get("message_sent", False):
            messages.success(self.request, f"Welcome back, {user.username}!")
            self.request.session["message_sent"] = True
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


class CustomLogoutView(LogoutView):
    """Handle user logout."""
    template_name = "account/logout.html"
    next_page = reverse_lazy("home:index")

    def dispatch(self, request, *_args, **_kwargs):
        if request.method == "POST":
            if not self.request.session.get("message_sent", False):
                messages.success(
                    request, "You have been logged out successfully.")
                self.request.session["message_sent"] = True
            logout(request)
            return HttpResponseRedirect(self.get_next_page())
        return self.render_to_response(self.get_context_data())

    def get_next_page(self):
        return str(self.next_page)


class CustomPasswordResetView(PasswordResetView):
    template_name = 'account/password_reset.html'
    email_template_name = 'account/email/password_reset_key_message.txt'
    success_url = reverse_lazy('accounts:password_reset_done')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'site_name': 'MasteryHub',
            'domain': '127.0.0.1:8000' if self.request.is_secure() else '127.0.0.1:8000',
            'protocol': 'https' if self.request.is_secure() else 'http',
        })
        return context

    def form_valid(self, form):
        self.extra_email_context = {
            'site_name': 'MasteryHub',
            'domain': '127.0.0.1:8000' if self.request.is_secure() else '127.0.0.1:8000',
            'protocol': 'https' if self.request.is_secure() else 'http',
        }
        return super().form_valid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'account/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'account/password_reset_from_key.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    form_class = CustomSetPasswordForm


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'account/password_reset_complete.html'


class CustomSocialLoginCancelledView(LoginCancelledView):
    """Handle cancelled social logins."""

    def get(self, request, *args, **kwargs):
        messages.error(
            request,
            "Social login was cancelled. Please try again or use your MasteryHub account."
        )
        return redirect("accounts:login")


class CustomSocialLoginErrorView(RedirectView):
    """Handle social login errors."""

    permanent = False
    query_string = True
    pattern_name = 'accounts:login'

    def get(self, request, *args, **kwargs):
        messages.error(
            request,
            "There was an error with your social login. Please try again or use your MasteryHub account."
        )
        return super().get(request, *args, **kwargs)


class CustomGoogleCallbackView(View):
    """Custom callback view for Google OAuth2."""
    adapter_class = GoogleOAuth2Adapter

    def get(self, request, *args, **kwargs):
        try:
            adapter = self.adapter_class(request)
            provider = adapter.get_provider()
            app = provider.app
            
            # Get the authorization code from the request
            code = request.GET.get('code')
            if not code:
                messages.error(request, 'No authorization code received from Google.')
                return redirect('accounts:login')
            
            # Get the state parameter to prevent CSRF
            state = request.GET.get('state')
            if not state or state != request.session.get('oauth2_state'):
                messages.error(request, 'Invalid OAuth2 state. Please try again.')
                return redirect('accounts:login')
            
            # Get the access token
            token = adapter.get_access_token(request, code)
            if not token:
                messages.error(request, 'Failed to get access token from Google.')
                return redirect('accounts:login')
            
            # Get user info
            user_info = adapter.get_user_info(request, token)
            if not user_info:
                messages.error(request, 'Failed to get user info from Google.')
                return redirect('accounts:login')
            
            # Get or create social account
            social_account, created = SocialAccount.objects.get_or_create(
                provider='google',
                uid=user_info['id'],
                defaults={
                    'user': request.user if request.user.is_authenticated else None,
                    'extra_data': user_info
                }
            )
            
            if not social_account.user:
                messages.error(request, 'Please sign in first before connecting your Google account.')
                return redirect('accounts:login')
            
            # Log the user in
            login(request, social_account.user)
            messages.success(request, 'Successfully connected your Google account!')
            return redirect('home:index')
            
        except Exception as e:
            logger.error(f"Google OAuth callback error: {str(e)}")
            messages.error(request, f'An error occurred during Google authentication: {str(e)}')
            return redirect('accounts:login')
