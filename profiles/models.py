from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=255, blank=True)
    goals = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True)
    linkedin_profile = models.URLField(blank=True, null=True)
    github_profile = models.URLField(null=True, blank=True)
    is_expert = models.BooleanField(default=False)
    mentor_since = models.DateField(null=True, blank=True)
    mentorship_areas = models.CharField(
        max_length=255,
        blank=True,
        default=''
    )
    availability = models.CharField(
        max_length=255,
        blank=True,
        default=''
    )
    preferred_mentoring_method = models.CharField(
        max_length=100,
        blank=True,
        default='One-on-one'
    )
    is_available = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.user.username

    class Meta:
        unique_together = ("user",)
        indexes = [models.Index(fields=["user"])]
