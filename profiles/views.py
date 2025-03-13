from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile
from .forms import ProfileForm, UserForm
from django.contrib.auth import get_user_model
from django.db import transaction
import logging

# Create your views here.

User = get_user_model()
logger = logging.getLogger(__name__)


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
    """Edit the user's profile with enhanced error handling and logging."""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        logger.error(
            f"Profile does not exist for user: {request.user.username}")
        messages.error(
            request, "Your profile does not exist. Please contact support.")
        return redirect('home:index')

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            try:
                with transaction.atomic():
                    user_form.save()
                    profile_form.save()
                    messages.success(
                        request, 'Your profile has been updated successfully!')
                    return redirect('profiles:view_profile', username=request.user.username)
            except Exception as e:
                logger.error(
                    f"Error updating profile for user {request.user.username}: {str(e)}")
                messages.error(
                    request, "An error occurred while updating your profile. Please try again.")
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'profile': profile,
    }

    return render(request, 'profiles/edit_profile.html', context)


@login_required
def delete_profile(request):
    """Delete the user's profile and account."""
    if request.method == 'POST':
        with transaction.atomic():
            try:
                profile = request.user.profile

                if profile:
                    profile.delete()

                request.user.delete()

                messages.success(
                    request, "Your account has been deleted successfully.")
                return redirect('home:index')

            except Exception as e:
                messages.error(
                    request, "An error occurred while deleting your account.")
                return redirect('profiles:view_profile')

    return render(request, 'profiles/delete_confirmation.html', {
        'user': request.user
    })
