from django.contrib.auth.models import User
from django.db import models
from profiles.models import Profile
from datetime import timedelta
from django.utils import timezone

# Create your models here.


class Session(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    duration = models.DurationField(default=timedelta(hours=1))
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    host = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="sessions_hosted"
    )
    participants = models.ManyToManyField(
        Profile, related_name="sessions_participated", blank=True
    )
    category = models.ForeignKey(
        "Category", on_delete=models.SET_NULL, null=True)
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
    image = models.ImageField(
        upload_to="session_images/", null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

    @property
    def current_participants(self):
        return self.participants.count()

    def is_full(self):
        return self.current_participants >= self.max_participants

    @property
    def available_spots(self):
        return self.max_participants - self.current_participants

    @property
    def total_duration(self):
        return self.duration


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
        Session, on_delete=models.CASCADE, related_name="reviews")
    reviewer = models.ForeignKey(Profile, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer.user.username}'s review for {self.session.title}"


class Forum(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_post = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="comments"
    )

    def __str__(self):
        return self.title


class Feedback(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    mentee = models.ForeignKey(
        Profile, related_name="feedbacks", on_delete=models.CASCADE)
    mentor = models.ForeignKey(
        Profile, related_name="given_feedbacks", on_delete=models.CASCADE)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class ConcernReport(models.Model):
    CATEGORY_CHOICES = [
        ("inappropriate_behavior", "Inappropriate Behavior"),
        ("technical_issue", "Technical Issue"),
        ("content_quality", "Content Quality"),
        ("other", "Other"),
    ]

    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_category_display()} - {self.created_at}"


class Skill(models.Model):
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='skills',
        default=1
    )
    price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, default=1)
    booking_date = models.DateTimeField()
    status = models.CharField(max_length=20)
    scheduled_time = models.DateTimeField(null=True, blank=True)
    session = models.ForeignKey(
        Session, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"Booking by {self.user.username} for {self.skill.title}"


class LearningGoal(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Mentor(models.Model):
    EXPERIENCE_LEVELS = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    rating = models.DecimalField(
        max_digits=3, decimal_places=2, null=True, blank=True)
    is_available = models.BooleanField(default=False)
    skills = models.ManyToManyField(Skill, related_name='mentors')
    categories = models.ManyToManyField(Category, related_name='mentors')
    experience_level = models.CharField(
        max_length=20, choices=EXPERIENCE_LEVELS, default='intermediate')
    hourly_rate = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Mentor Profile"
