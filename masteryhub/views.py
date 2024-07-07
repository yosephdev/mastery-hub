from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import CustomSignupForm, CustomUserChangeForm
from .forms import ProfileForm
from .models import Profile


# Create your views here.


def home(request):
    return render(request, "masteryhub/index.html")


def signup_view(request):
    if request.method == "POST":
        form = CustomSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password1")
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(
                request, f"Welcome, {user.username}! Registration successful!"
            )
            return redirect("home")
    else:
        form = CustomSignupForm()
    return render(request, "account/signup.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "account/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        existing_messages = [
            m for m in messages.get_messages(self.request) if "Welcome back" in str(m)
        ]
        if not existing_messages:
            messages.success(
                self.request, f"Welcome back, {self.request.user.username}!"
            )
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)


class CustomLogoutView(LogoutView):
    template_name = "account/logout.html"
    next_page = reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        if request.method == "POST":
            messages.success(request, "You have been logged out successfully.")
            logout(request)
            return HttpResponseRedirect(self.get_next_page())
        elif request.method == "GET":
            return self.render_to_response(self.get_context_data())

    def get_next_page(self):
        return str(self.next_page)


@login_required
def view_profile(request, username=None):
    if username:
        profile = get_object_or_404(Profile, user__username=username)
    else:
        profile = request.user.profile
    return render(request, "masteryhub/view_profile.html", {"profile": profile})


@login_required
def edit_profile(request):
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("view_profile")
    else:
        form = ProfileForm(instance=profile)
    return render(request, "masteryhub/edit_profile.html", {"form": form})


def view_mentor_profile(request, username):
    profile = get_object_or_404(Profile, user__username=username, is_expert=True)
    return render(request, "masteryhub/view_mentor_profile.html", {"profile": profile})
