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
from allauth.account.views import ConfirmEmailView
from allauth.account.models import EmailConfirmationHMAC, EmailAddress
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
from accounts.forms import CustomSetPasswordForm
import logging
from allauth.socialaccount.views import LoginCancelledView
from allauth.socialaccount.models import SocialLogin
from django.views.generic import RedirectView, View
from allauth.socialaccount.providers.oauth2.views import OAuth2CallbackView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter

from .forms import (
    CustomSignupForm,
    CustomSetPasswordForm,
)

logger = logging.getLogger(__name__)


@csrf_exempt
def signup_view(request):
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Check if user already exists with this email
                    email = form.cleaned_data.get('email')
                    if EmailAddress.objects.filter(email=email).exists():
                        messages.error(
                            request, "An account with this email already exists. Please use a different email or try to log in.")
                        return render(request, "account/signup.html", {"form": form})
                    
                    # Create the user
                    user = form.save()
                    raw_password = form.cleaned_data.get('password1')
                    authenticated_user = authenticate(
                        username=user.username, password=raw_password)
                    
                    if authenticated_user is not None:
                        auth_login(request, authenticated_user)
                        
                        # Send confirmation email
                        try:
                            send_confirmation_email(user, request)
                            messages.success(
                                request, 
                                f"Welcome to MasteryHub, {user.username}! Your account has been created successfully. "
                                f"We've sent a verification email to {user.email}. Please check your inbox and verify your email address."
                            )
                        except Exception as email_error:
                            logger.error(f"Email sending error: {str(email_error)}")
                            messages.warning(
                                request, 
                                f"Your account was created, but we couldn't send the verification email. "
                                f"Please contact support if you don't receive a verification email soon."
                            )
                        
                        return redirect("home:index")
            except Exception as e:
                logger.error(f"Signup error: {str(e)}")
                messages.error(
                    request, "There was an error creating your account. Please try again.")
                return redirect("accounts:signup")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{error}")
    else:
        form = CustomSignupForm()
    return render(request, "account/signup.html", {"form": form})


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
                messages.error(request, "The confirmation link has expired. Please request a new one.")
                return redirect("accounts:login")
            return super().dispatch(request, *args, **kwargs)
        except Http404:
            messages.error(request, "Invalid confirmation link. Please request a new one.")
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
            messages.error(request, "There was an error confirming your email. Please try again or contact support.")
            return redirect("accounts:login")


def send_confirmation_email(user, request):
    current_site = get_current_site(request)
    subject = 'Confirm Your MasteryHub Email Address'
    
    # Create email confirmation for the user
    email_address, created = EmailAddress.objects.get_or_create(
        user=user,
        email=user.email,
        defaults={'verified': False, 'primary': True}
    )
    
    # Generate confirmation key
    email_confirmation = EmailConfirmationHMAC(email_address)
    
    # Generate confirmation URL
    protocol = 'https' if request.is_secure() else 'http'
    activate_url = f"{protocol}://{current_site.domain}/accounts/confirm-email/{email_confirmation.key}/"
    
    # Set site name and domain
    current_site.name = "MasteryHub"
    
    # Render email template with context
    message = render_to_string('account/email/email_confirmation_message.html', {
        'user': user,
        'current_site': current_site,
        'domain': current_site.domain,
        'activate_url': activate_url,
        'expiry_days': 3,
        'site_name': "MasteryHub"
    })
    
    # Create plain text version
    text_message = render_to_string('account/email/email_confirmation_message.txt', {
        'user': user,
        'current_site': current_site,
        'domain': current_site.domain,
        'activate_url': activate_url,
        'site_name': "MasteryHub"
    })
    
    # Send the email
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
        messages.error(
            self.request,
            "Login failed. Please check your username and password."
        )
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
    template_name = "account/login.html"
    
    def dispatch(self, request, *args, **kwargs):
        # Set a session flag to indicate this is a social login
        request.session['is_social_login'] = True
        request.session['sociallogin_provider'] = 'google'
        
        # Log the callback
        logger.info("Google OAuth callback received")
        
        try:
            # Create an instance of OAuth2CallbackView
            oauth2_view = OAuth2CallbackView()
            oauth2_view.adapter_class = self.adapter_class
            
            # Call the parent dispatch method
            response = oauth2_view.dispatch(request, *args, **kwargs)
            
            # If the user is authenticated, add a success message
            if request.user.is_authenticated:
                # Mark the user's email as verified
                try:
                    email_address, created = EmailAddress.objects.get_or_create(
                        user=request.user,
                        email=request.user.email,
                        defaults={'verified': True, 'primary': True}
                    )
                    
                    if not email_address.verified:
                        email_address.verified = True
                        email_address.save()
                except Exception as e:
                    logger.error(f"Error verifying email: {str(e)}")
                
                messages.success(
                    request, 
                    f"Welcome, {request.user.username or request.user.email}! You've successfully signed in with Google."
                )
                
            return response
        except Exception as e:
            # Log the error
            logger.error(f"Google OAuth callback error: {str(e)}")
            
            # Add an error message
            messages.error(
                request, 
                "There was an error with your Google login. Please try again or use your MasteryHub account."
            )
            
            # Redirect to login page
            return redirect("accounts:login")
