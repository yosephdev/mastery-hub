from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from masteryhub.models import Session, Category
from profiles.models import Profile
from decimal import Decimal
import random
from datetime import timedelta

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates sample learning sessions for testing'

    def handle(self, *args, **kwargs):
        try:            
            Session.objects.all().delete()

            categories = Category.objects.all()
            if not categories:
                self.stdout.write(self.style.ERROR(
                    'Please create categories first'))
                return

            expert_profiles = Profile.objects.filter(is_expert=True)
            if not expert_profiles:
                self.stdout.write(self.style.ERROR('No expert profiles found'))
                return

            session_titles = [
                "Introduction to Programming",
                "Web Development Basics",
                "Data Analysis Workshop",
                "Python for Beginners",
                "JavaScript Fundamentals",
                "Database Design",
                "Mobile App Development",
                "Software Testing Basics"
            ]

            for profile in expert_profiles:
                Session.objects.create(
                    title=random.choice(session_titles),
                    description="Learn essential skills in this interactive session",
                    duration=timedelta(hours=random.choice([1, 2, 3])),
                    price=Decimal(random.choice(['49.99', '79.99', '99.99'])),
                    host=profile,
                    category=random.choice(categories),
                    status="scheduled",
                    max_participants=random.randint(5, 15),
                    is_active=True
                )
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created session for {profile.user.username}')
                )

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
