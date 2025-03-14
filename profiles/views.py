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
def delete_profile(request, user_id=None):
    """Delete the user's profile and account."""
    # Ensure the user is trying to delete their own profile or is an admin
    if user_id and user_id != request.user.id and not request.user.is_staff:
        messages.error(request, "You can only delete your own account.")
        return redirect('profiles:view_profile', username=request.user.username)
    
    # If user_id is provided and user is admin, use that ID, otherwise use the current user's ID
    target_user_id = user_id if user_id and request.user.is_staff else request.user.id
    
    try:
        # Get the user to delete
        target_user = get_object_or_404(User, id=target_user_id)
    except Exception as e:
        logger.error(f"Error finding user with ID {target_user_id}: {str(e)}")
        messages.error(request, "User not found.")
        return redirect('home:index')
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Try to get the profile, but don't error if it doesn't exist
                try:
                    profile = target_user.profile
                    profile.delete()
                    logger.info(f"Profile deleted for user {target_user.username}")
                except Profile.DoesNotExist:
                    # Profile doesn't exist, just continue to delete the user
                    logger.info(f"No profile found for user {target_user.username}")
                    pass
                except Exception as profile_error:
                    logger.error(f"Error deleting profile for user {target_user.username}: {str(profile_error)}")
                    # Continue to delete the user even if profile deletion fails
                
                # Delete the user
                username = target_user.username
                target_user.delete()
                logger.info(f"User {username} deleted successfully")
                
                messages.success(request, "The account has been deleted successfully.")
                
                # If the user deleted their own account, redirect to home
                if target_user_id == request.user.id:
                    return redirect('home:index')
                # If admin deleted another user, redirect to admin dashboard or profiles list
                return redirect('profiles:view_profiles')
        except Exception as e:
            logger.error(f"Error deleting user {target_user.username}: {str(e)}")
            messages.error(request, f"An error occurred while deleting the account: {str(e)}")
            return redirect('profiles:view_profile', username=target_user.username)

    return render(request, 'profiles/delete_confirmation.html', {
        'user': target_user
    })
