from django.http import HttpResponseRedirect, Http404
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
from allauth.account.models import EmailConfirmationHMAC
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt
import logging

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
                    user = form.save()
                    raw_password = form.cleaned_data.get('password1')
                    authenticated_user = authenticate(
                        username=user.username, password=raw_password)
                    if authenticated_user is not None:
                        auth_login(request, authenticated_user)
                        messages.success(
                            request, f"Welcome to MasteryHub, {user.username}! Your account has been created successfully.")
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
