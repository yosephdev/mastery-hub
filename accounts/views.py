from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views import View
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q, Count, Sum
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.utils import timezone
from django.contrib.auth.models import User
from .forms import MentorApplicationForm, ConcernReportForm
from django.contrib.admin.models import LogEntry, ADDITION
from allauth.account.views import ConfirmEmailView
from allauth.account.models import EmailConfirmationHMAC
from django.contrib.contenttypes.models import ContentType

from profiles.models import Profile
from checkout.models import Payment, Cart, CartItem, Order
from masteryhub.models import Feedback, Session, Category, Mentorship
from .forms import CustomSignupForm, CustomUserChangeForm
from checkout.forms import OrderForm
import stripe
import json
import logging

# Create your views here.


def signup_view(request):
    """Handle user signup."""
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(request)
                username = form.cleaned_data.get("username")
                password = form.cleaned_data.get("password1")
                user = authenticate(username=username, password=password)

                if user is not None:
                    auth_login(request, user)
                    messages.success(
                        request,
                        f"Welcome, {user.username}! Registration successful!"
                    )
                    return redirect("home")
                else:
                    messages.error(request, "Authentication failed.")
            except Exception as e:
                messages.error(request, f"An error occurred: {str(e)}")
        else:
            for field, error in form.errors.items():
                messages.error(request, f"{field}: {error}")
    else:
        form = CustomSignupForm()

    return render(request, "account/signup.html", {"form": form})


class CustomConfirmEmailView(ConfirmEmailView):
    template_name = "account/email_confirm.html"

    def get_object(self, queryset=None):
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
        user = form.get_user()
        auth_login(self.request, user)
        if not self.request.session.get("message_sent", False):
            messages.success(self.request, f"Welcome back, {user.username}!")
            self.request.session["message_sent"] = True
        if user.is_superuser:
            return redirect("admin:index")
        elif user.profile.is_expert:
            return redirect("view_mentor_profile", username=user.username)
        else:
            return redirect("view_profile", username=user.username)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "Login failed. Please check your username and password."
        )
        return self.render_to_response(self.get_context_data(form=form))


class CustomLogoutView(LogoutView):
    """Handle user logout."""

    template_name = "account/logout.html"
    next_page = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            if not self.request.session.get("message_sent", False):
                messages.success(request, "You have been logged out successfully.")
                self.request.session["message_sent"] = True
            logout(request)
            return HttpResponseRedirect(self.get_next_page())
        return self.render_to_response(self.get_context_data())

    def get_next_page(self):
        return str(self.next_page)
