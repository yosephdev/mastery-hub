from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.views import View
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import login as auth_login
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Q, Count, Sum
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from masteryhub.forms import MentorApplicationForm, ConcernReportForm
from django.contrib.admin.models import LogEntry, ADDITION
from django.contrib.contenttypes.models import ContentType
from .models import Profile

# Create your views here.

def get_user_profile(username):
    """A view that handles the get user profile."""
    return get_object_or_404(Profile, user__username=username)


@login_required
def view_profile(request, username=None):
    """A view that handles the view profile."""
    if username:
        profile = get_object_or_404(Profile, user__username=username)
        is_own_profile = request.user.username == username
    else:
        profile, created = Profile.objects.get_or_create(user=request.user)
        is_own_profile = True

    context = {
        "profile": profile,
        "is_own_profile": is_own_profile,
        "has_profile_picture": bool(profile.profile_picture),
    }

    template = (
        "profiles/view_mentor_profile.html"
        if profile.is_expert
        else "profiles/view_mentee_profile.html"
    )
    return render(request, template, context)

@login_required
def edit_profile(request):
    """A view that handles the edit profile."""
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("view_profile", username=profile.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, "profiles/edit_profile.html", {"form": form})
    
def view_mentor_profile(request, username):
    """A view that handles the view mentor pofile."""
    profile = get_object_or_404(Profile, user__username=username, is_expert=True)
    is_own_profile = (
        request.user.username == username if request.user.is_authenticated else False
    )
    context = {
        "profile": profile,
        "is_own_profile": is_own_profile,
    }
    return render(request, "profiles/view_mentor_profile.html", context)