from django.contrib.auth.models import User
from django.db import models

# Create your models here.


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
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


class Session(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField()
    duration = models.DurationField()
    host = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="sessions_hosted"
    )
    participants = models.ManyToManyField(
        Profile, related_name="sessions_participated", blank=True
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
    image = models.ImageField(upload_to="session_images/", null=True, blank=True)

    def __str__(self):
        return self.title

    @property
    def current_participants(self):
        return self.participants.count()

    @property
    def available_spots(self):
        return self.max_participants - self.current_participants

    @property
    def classes_count(self):
        return 1

    @property
    def total_duration(self):
        return self.duration * self.classes_count


class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Mentorship(models.Model):
    mentor = models.ForeignKey(
        Profile, related_name="mentorships_as_mentor", on_delete=models.CASCADE
    )
    mentee = models.ForeignKey(
        Profile, related_name="mentorships_as_mentee", on_delete=models.CASCADE
    )
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(blank=True, null=True)
    goals = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "Pending"),
            ("accepted", "Accepted"),
            ("rejected", "Rejected"),
            ("completed", "Completed"),
        ],
        default="pending",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mentor.user.username} mentoring {self.mentee.user.username} - {self.status}"


class Review(models.Model):
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.user.username}'s review for {self.session.title}"


class Payment(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    session = models.ForeignKey(
        Session, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"{self.user.user.username} - {self.amount} on {self.date}"


class Forum(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_post = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="comments"
    )

    def __str__(self):
        return self.title


class Feedback(models.Model):
    mentee = models.ForeignKey(
        Profile, related_name="feedbacks", on_delete=models.CASCADE
    )
    mentor = models.ForeignKey(
        Profile, related_name="given_feedbacks", on_delete=models.CASCADE
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
