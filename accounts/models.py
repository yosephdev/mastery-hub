from django.contrib.auth.models import User
from django.db import models
from datetime import timedelta

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=255, blank=True)
    goals = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True
    )
    linkedin_profile = models.URLField(blank=True)
    github_profile = models.URLField(blank=True)
    is_expert = models.BooleanField(default=False)
    mentor_since = models.DateField(null=True, blank=True)
    mentorship_areas = models.TextField(
        blank=True, help_text="Areas you're willing to mentor in, separated by commas"
    )
    availability = models.CharField(
        max_length=255, blank=True, help_text="Your general availability for mentoring"
    )
    preferred_mentoring_method = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., One-on-one, Group sessions, Online, In-person",
    )

    def __str__(self):
        return self.user.username

    class Meta:
        unique_together = ("user",)
        indexes = [models.Index(fields=["user"])]
