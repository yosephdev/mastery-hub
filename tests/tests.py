import os
import django
from django.test.utils import setup_test_environment

os.environ["DJANGO_SETTINGS_MODULE"] = "skill_sharing_platform.settings"

django.setup()
setup_test_environment()

import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from masteryhub.models import Session, Category
from accounts.models import Profile
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

        # Follow redirect if status code is 301 or 302
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

        # Follow redirect if status code is 301 or 302
        while response.status_code in (301, 302):
            response = self.client.get(response.url)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json().get("success"))
        self.assertEqual(len(self.client.session.get("cart", [])), 0)
