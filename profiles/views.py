from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from .models import Profile
from .forms import ProfileForm

# Create your views here.


def get_user_profile(username):
    """Retrieve a user profile by username."""
    return get_object_or_404(Profile, user__username=username)


@login_required
def view_profiles(request):
    """View all user profiles."""
    query = request.GET.get('q')
    if query:
        profiles = Profile.objects.filter(user__username__icontains=query)
    else:
        profiles = Profile.objects.all()
    return render(request, "profiles/list_profiles.html", {"profiles": profiles})


@login_required
def view_profile(request, username=None):
    """View the user's profile or a specific user's profile."""
    if username:
        profile = get_object_or_404(Profile, user__username=username)
        is_own_profile = request.user.username == username
    else:
        profile = request.user.profile
        is_own_profile = True

    context = {
        "profile": profile,
        "is_own_profile": is_own_profile,
        "has_profile_picture": bool(profile.profile_picture),
    }

    if profile.is_expert:
        return render(request, "profiles/view_mentor_profile.html", context)
    return render(request, "profiles/view_profile.html", context)


@login_required
def edit_profile(request):
    """Edit the user's profile."""
    profile = request.user.profile
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Your profile has been updated successfully.")
            return redirect("view_profile", username=profile.user.username)
    else:
        form = ProfileForm(instance=profile)
    return render(request, "profiles/edit_profile.html", {"form": form})


@login_required
def view_mentor_profile(request, username):
    """View a mentor's profile."""
    profile = get_object_or_404(
        Profile, user__username=username, is_expert=True)
    is_own_profile = request.user.username == username if request.user.is_authenticated else False
    context = {
        "profile": profile,
        "is_own_profile": is_own_profile,
    }
    return render(request, "profiles/view_mentor_profile.html", context)


@login_required
def delete_profile(request):
    """Delete the current user's profile."""
    if request.method == 'POST':
        user = request.user
        user.delete()
        messages.success(
            request, "Your profile has been deleted successfully.")
        return redirect('home:index')

    return render(request, 'profiles/delete_confirmation.html')
