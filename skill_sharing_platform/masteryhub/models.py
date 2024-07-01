from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=255, blank=True)
    experience = models.TextField(blank=True)
    achievements = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class Session(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    duration = models.DurationField()
    host = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="sessions_hosted"
    )
    participants = models.ManyToManyField(
        User, related_name="sessions_participated", blank=True
    )

    def __str__(self):
        return self.title


class Mentorship(models.Model):
    mentor = models.ForeignKey(
        User, related_name="mentorships_as_mentor", on_delete=models.CASCADE
    )
    mentee = models.ForeignKey(
        User, related_name="mentorships_as_mentee", on_delete=models.CASCADE
    )
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    goals = models.TextField(blank=True)

    def __str__(self):
        return f"{self.mentor.username} mentoring {self.mentee.username}"
