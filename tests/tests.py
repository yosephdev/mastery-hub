import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from masteryhub.models import Session, Profile, Category
from datetime import datetime, timedelta


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

    def test_add_to_bag(self):
        response = self.client.post(
            reverse("add_to_bag"),
            data=json.dumps(
                {
                    "session_id": self.session.id,
                    "title": self.session.title,
                    "price": self.session.price,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))
        self.assertEqual(len(self.client.session.get("bag", [])), 1)

    def test_remove_from_bag(self):
        self.client.session["bag"] = [
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
            reverse("remove_from_bag"),
            data=json.dumps({"session_id": self.session.id}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))
        self.assertEqual(len(self.client.session.get("bag", [])), 0)
