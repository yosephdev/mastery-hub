from django.db.models.signals import post_save
from django.db.models.signals import post_delete
from django.dispatch import receiver
from allauth.account.signals import user_logged_in, user_logged_out
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile


@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        profile = getattr(instance, "profile", None)
        if profile:
            profile.save()


@receiver(post_delete, sender=User)
def delete_user_profile(sender, instance, **kwargs):
    instance.profile.delete()


@receiver(user_logged_in)
def user_logged_in_message(sender, request, user, **kwargs):
    messages.success(request, f"Welcome back, {user.username}!")


@receiver(user_logged_out)
def user_logged_out_message(sender, request, user, **kwargs):
    messages.info(request, "You have been logged out successfully.")
