from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from profiles.models import Profile
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a user profile when a new user is created."""
    if created:
        # Check if profile already exists before creating
        if not Profile.objects.filter(user=instance).exists():
            logger.info(f"Creating profile for new user: {instance.username}")
            Profile.objects.create(
                user=instance,
                bio='',
                skills='',
                goals='',
                experience='',
                achievements='',
                mentorship_areas='',
                availability='',
                preferred_mentoring_method='One-on-one',
                is_available=True,
                github_profile=None
            )
        else:
            logger.warning(f"Profile already exists for user: {instance.username}")


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the user profile when the user is saved."""
    try:
        profile = instance.profile
        profile.save()
    except Profile.DoesNotExist:
        # Only create a profile if it doesn't exist
        if not Profile.objects.filter(user=instance).exists():
            logger.info(f"Creating missing profile for existing user: {instance.username}")
            Profile.objects.create(
                user=instance,
                bio='',
                skills='',
                goals='',
                experience='',
                achievements='',
                mentorship_areas='',
                availability='',
                preferred_mentoring_method='One-on-one',
                is_available=True,
                github_profile=None
            )
