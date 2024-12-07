from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from .models import Profile
from .forms import ProfileForm
from django.contrib.auth import get_user_model

# Create your views here.

User = get_user_model()


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
    # Get or create profile
    profile, created = Profile.objects.get_or_create(
        user=request.user,
        defaults={
            'bio': '',
            'skills': '',
            'goals': '',
            'experience': '',
            'achievements': '',
            'mentorship_areas': '',
            'availability': '',
            'preferred_mentoring_method': '',
            'is_available': True
        }
    )

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)

    context = {
        'form': form,
        'profile': profile,
        'created': created
    }

    if created:
        messages.info(request, 'A new profile has been created for you. Please fill in your details.')

    return render(request, 'profiles/edit_profile.html', context)


@login_required
def view_mentor_profile(request, username):
    """View a mentor's profile."""
    try:
        user = get_object_or_404(User, username=username)

        profile, created = Profile.objects.get_or_create(
            user=user,
            defaults={
                'is_expert': True,
                'bio': f"Welcome to {username}'s profile"
            }
        )

        if not profile.is_expert:
            messages.error(request, "This user is not registered as a mentor.")
            return redirect('home:index')

        is_own_profile = request.user.username == username

        context = {
            "profile": profile,
            "is_own_profile": is_own_profile,
        }

        return render(request, "profiles/view_mentor_profile.html", context)

    except User.DoesNotExist:
        messages.error(request, "This user does not exist.")
        return redirect('home:index')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('home:index')


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
