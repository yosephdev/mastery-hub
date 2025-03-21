from django.db import connection
from datetime import datetime, timedelta
from django.contrib.sessions.models import Session
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from masteryhub.models import Category, Skill, Booking
import os
import django
from django.test import TransactionTestCase

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "skill_sharing_platform.settings")
django.setup()

try:
    from profiles.models import Profile
except ImportError:
    raise ImportError(
        "Could not import Profile model. Is the profiles app in INSTALLED_APPS?")

def tearDown(self):
    if hasattr(self, 'user'):
        self.user.delete()
    Profile.objects.filter(user=self.user).delete()


class SkillModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Tech")
        self.user = User.objects.create_user(
            username='testuser', password='testpass123')

    def test_skill_creation(self):
        skill = Skill.objects.create(
            name="Python Basics",
            title="Python Programming",
            category=self.category,
            price=50.00,
            description="Learn Python"
        )
        self.assertEqual(skill.title, "Python Programming")
        self.assertEqual(skill.category, self.category)

    def test_skill_retrieval(self):
        skill = Skill.objects.create(
            name="Python Basics",
            title="Python Programming",
            category=self.category,
            price=50.00,
            description="Learn Python"
        )
        retrieved_skill = Skill.objects.get(id=skill.id)
        self.assertEqual(retrieved_skill.title, "Python Programming")

    def test_skill_update(self):
        skill = Skill.objects.create(
            name="Python Basics",
            title="Python Programming",
            category=self.category,
            price=50.00,
            description="Learn Python"
        )
        skill.title = "Advanced Python"
        skill.save()
        self.assertEqual(skill.title, "Advanced Python")

    def test_skill_deletion(self):
        skill = Skill.objects.create(
            name="Python Basics",
            title="Python Programming",
            category=self.category,
            price=50.00,
            description="Learn Python"
        )
        skill_id = skill.id
        skill.delete()
        with self.assertRaises(Skill.DoesNotExist):
            Skill.objects.get(id=skill_id)

    def test_invalid_skill_creation(self):
        with self.assertRaises(ValidationError):
            skill = Skill(title="", description="Learn Python",
                          category=self.category, price=50)
            skill.full_clean()


class BookingModelTest(TransactionTestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Tech")
        self.user = User.objects.create_user(
            username='testuser', password='testpass123')
        self.skill = Skill.objects.create(
            name="Python Basics",
            title="Python Programming",
            category=self.category,
            price=50.00,
            description="Learn Python"
        )
        self.booking_date = timezone.now()

    def test_booking_creation(self):
        booking = Booking.objects.create(
            user=self.user,
            skill=self.skill,
            booking_date=self.booking_date,
            status="confirmed"
        )
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.skill, self.skill)
        self.assertEqual(booking.status, "confirmed")

    def test_booking_retrieval(self):
        booking = Booking.objects.create(
            user=self.user,
            skill=self.skill,
            booking_date=self.booking_date,
            status="confirmed"
        )
        retrieved_booking = Booking.objects.get(id=booking.id)
        self.assertEqual(retrieved_booking.user, booking.user)
        self.assertEqual(retrieved_booking.skill, booking.skill)
        self.assertEqual(retrieved_booking.status, booking.status)

    def test_booking_update(self):
        booking = Booking.objects.create(
            user=self.user,
            skill=self.skill,
            booking_date=self.booking_date,
            status="confirmed"
        )
        booking.status = "canceled"
        booking.save()
        updated_booking = Booking.objects.get(id=booking.id)
        self.assertEqual(updated_booking.status, "canceled")

    def test_booking_deletion(self):
        booking = Booking.objects.create(
            user=self.user,
            skill=self.skill,
            booking_date=self.booking_date,
            status="confirmed"
        )
        booking_id = booking.id
        booking.delete()
        with self.assertRaises(Booking.DoesNotExist):
            Booking.objects.get(id=booking_id)

    def test_invalid_booking_creation(self):
        with self.assertRaises(ValidationError):
            booking = Booking(user=None, skill=None,
                              booking_date=self.booking_date, status="confirmed")
            booking.full_clean()


class BagViewTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123')
        Profile.objects.get_or_create(user=self.user, defaults={
                                      "bio": "Test bio"})  # Ensuring unique profile
        self.category = Category.objects.create(name="Tech")
        self.skill = Skill.objects.create(
            name="Python Basics",
            title="Python Programming",
            category=self.category,
            price=50.00,
            description="Learn Python"
        )
        self.client.login(username='testuser', password='testpass123')

        self.profile, created = Profile.objects.get_or_create(
            user=self.user, defaults={"bio": "Test bio"}
        )

        self.session = Session.objects.create(
            title="Test Session",
            description="This is a test session",
            price=100.0,
            duration=timedelta(hours=1),
            date=datetime.now(),
            host=self.profile,
            category=self.category,
        )

        self.session_id = self.session.id

    def tearDown(self):
        # Ensure profiles are cleaned up
        Profile.objects.filter(user=self.user).delete()
        self.user.delete()

    def test_add_to_cart(self):
        url = reverse("checkout:add_to_cart", args=[self.skill.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301)

    def test_remove_from_cart(self):
        url = reverse("checkout:remove_from_cart", args=[self.skill.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 301)


class DatabaseConnectionTest(TestCase):
    def test_database_connection(self):
        try:
            conn = connection.cursor()
            conn.execute("SELECT 1")
            self.assertEqual(conn.fetchone()[0], 1)
            print("Database connection successful.")
        except Exception as e:
            self.fail(f"Database connection failed: {e}")
