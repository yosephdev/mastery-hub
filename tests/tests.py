import os
import django
import json
from datetime import datetime, timedelta

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from masteryhub.models import Session, Category, Skill, Booking
from accounts.models import Profile
from django.core.exceptions import ValidationError

os.environ["DJANGO_SETTINGS_MODULE"] = "skill_sharing_platform.settings"
django.setup()


class SkillModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")

    def test_skill_creation(self):
        skill = Skill.objects.create(
            title="Web Development",
            description="Learn Django",
            category="Tech",
            price=50,
            user=self.user
        )
        self.assertEqual(str(skill), "Web Development")
        self.assertEqual(skill.title, "Web Development")
        self.assertEqual(skill.description, "Learn Django")
        self.assertEqual(skill.category, "Tech")
        self.assertEqual(skill.price, 50)

    def test_skill_retrieval(self):
        skill = Skill.objects.create(
            title="Web Development",
            description="Learn Django",
            category="Tech",
            price=50,
            user=self.user
        )
        retrieved_skill = Skill.objects.get(id=skill.id)
        self.assertEqual(retrieved_skill.title, skill.title)
        self.assertEqual(retrieved_skill.description, skill.description)

    def test_skill_update(self):
        skill = Skill.objects.create(
            title="Web Development",
            description="Learn Django",
            category="Tech",
            price=50,
            user=self.user
        )
        skill.title = "Advanced Web Development"
        skill.save()
        updated_skill = Skill.objects.get(id=skill.id)
        self.assertEqual(updated_skill.title, "Advanced Web Development")

    def test_skill_deletion(self):
        skill = Skill.objects.create(
            title="Web Development",
            description="Learn Django",
            category="Tech",
            price=50,
            user=self.user
        )
        skill_id = skill.id
        skill.delete()
        with self.assertRaises(Skill.DoesNotExist):
            Skill.objects.get(id=skill_id)

    def test_invalid_skill_creation(self):
        with self.assertRaises(ValidationError):
            skill = Skill(title="", description="Learn Django", category="Tech", price=50)
            skill.full_clean()


class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.profile, created = Profile.objects.get_or_create(
            user=self.user, defaults={"bio": "Test bio"}
        )
        self.skill = Skill.objects.create(
            title="Web Development",
            description="Learn Django",
            category="Tech",
            price=50,
            user=self.user
        )

    def test_booking_creation(self):
        booking = Booking.objects.create(
            user=self.user,
            skill=self.skill,
            booking_date=datetime.now(),
            status="confirmed"
        )
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.skill, self.skill)
        self.assertEqual(booking.status, "confirmed")

    def test_booking_retrieval(self):
        booking = Booking.objects.create(
            user=self.user,
            skill=self.skill,
            booking_date=datetime.now(),
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
            booking_date=datetime.now(),
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
            booking_date=datetime.now(),
            status="confirmed"
        )
        booking_id = booking.id
        booking.delete()
        with self.assertRaises(Booking.DoesNotExist):
            Booking.objects.get(id=booking_id)

    def test_invalid_booking_creation(self):
        with self.assertRaises(ValidationError):
            booking = Booking(user=None, skill=None, booking_date=datetime.now(), status="confirmed")
            booking.full_clean()


class BagViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="testpass")
        self.client.login(username="testuser", password="testpass")

        self.profile, created = Profile.objects.get_or_create(
            user=self.user, defaults={"bio": "Test bio"}
        )

        self.category = Category.objects.create(
            name="Test Category", description="A category for testing"
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

    def test_add_to_cart(self):
        response = self.client.post(
            reverse("add_to_cart", args=[self.session.id]),
            data=json.dumps(
                {
                    "session_id": self.session.id,
                    "title": self.session.title,
                    "price": self.session.price,
                }
            ),
            content_type="application/json",
        )

        self.client.session.modified = True
        self.client.session.save()

        while response.status_code in (301, 302):
            response = self.client.get(response.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))
        self.assertEqual(len(self.client.session.get("cart", [])), 1)

    def test_remove_from_cart(self):
        self.client.session["cart"] = [
            {
                "session": {
                    "id": self.session.id,
                    "title": self.session.title,
                    "price": self.session.price,
                }
            }
        ]
        self.client.session.save()

        response = self.client.post(
            reverse("remove_from_cart", args=[self.session.id]),
            content_type="application/json",
        )

        while response.status_code in (301, 302):
            response = self.client.get(response.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))
        self.assertEqual(len(self.client.session.get("cart", [])), 0)
