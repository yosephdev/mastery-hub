from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from masteryhub.models import Mentor, Skill
from django.db import transaction
import random
from faker import Faker

fake = Faker()

SKILLS = [
    "Python Programming",
    "Web Development",
    "Data Analysis",
    "JavaScript",
    "React",
    "Django",
    "Database Design",
    "HTML/CSS",
    "Mobile Development",
    "UI/UX Design",
    "Project Management",
    "Agile Methodologies",
    "Software Testing",
    "Version Control"
]

EXPERIENCE_LEVELS = ['beginner', 'intermediate', 'advanced', 'expert']


class Command(BaseCommand):
    help = 'Creates sample mentors for testing'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int,
                            help='Number of mentors to create')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        total = kwargs['total']

        for skill_name in SKILLS:
            Skill.objects.get_or_create(
                title=skill_name,
                defaults={
                    'name': skill_name.lower().replace(' ', '_'),
                    'description': f"Knowledge and experience in {skill_name}"
                }
            )

        self.stdout.write(self.style.SUCCESS('Created sample skills'))

        for i in range(total):
            try:
                username = f"mentor_{i+1}_{fake.user_name()}"
                user = User.objects.create_user(
                    username=username[:30],
                    email=fake.email(),
                    password='testpass123'
                )
                user.first_name = fake.first_name()
                user.last_name = fake.last_name()
                user.save()

                mentor = Mentor.objects.create(
                    user=user,
                    bio=f"I am a {random.choice(EXPERIENCE_LEVELS)} level mentor specializing in various technologies.",
                    rating=round(random.uniform(3.5, 5.0), 1),
                    is_available=True,
                    experience_level=random.choice(EXPERIENCE_LEVELS),
                    hourly_rate=random.randint(20, 100)
                )

                available_skills = list(Skill.objects.all())
                selected_skills = random.sample(
                    available_skills, min(3, len(available_skills)))
                mentor.skills.set(selected_skills)

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created mentor: {user.get_full_name()}')
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error creating mentor {i+1}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {total} sample mentors')
        )
