from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    skills = models.CharField(max_length=255, blank=True)
    experience = models.TextField(blank=True)
    achievements = models.TextField(blank=True)
    profile_picture = models.ImageField(
        upload_to="profile_pics/", blank=True, null=True
    )
    linkedin_profile = models.URLField(blank=True)
    github_profile = models.URLField(blank=True)
    is_expert = models.BooleanField(default=False)

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
    category = models.ForeignKey("Category", on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("scheduled", "Scheduled"),
            ("ongoing", "Ongoing"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        default="scheduled",
    )
    max_participants = models.PositiveIntegerField(default=10)

    def __str__(self):
        return self.title


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


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


class Review(models.Model):
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.username}'s review for {self.session.title}"


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(
        Session, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.username} - {self.amount} on {self.date}"


class Subscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.CharField(
        max_length=20,
        choices=[("free", "Free"), ("basic", "Basic"), ("premium", "Premium")],
        default="free",
    )
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s {self.plan} subscription"
