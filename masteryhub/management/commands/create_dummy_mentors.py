from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from masteryhub.models import Mentor, Skill
from django.db import transaction
import random
from faker import Faker

fake = Faker()

SKILLS = [
    "AWS Cloud Services",
    "Azure Cloud Computing",
    "Blockchain Development",
    "Computer Vision",
    "Cybersecurity Fundamentals",
    "Data Science",
    "Digital Marketing",
    "Ethical Hacking",
    "Graphic Design",
    "IoT Development",
    "Machine Learning",
    "Podcast Production",
    "Video Production",
    "Web Development"
]

EXPERIENCE_LEVELS = ['beginner', 'intermediate', 'advanced', 'expert']


class Command(BaseCommand):
    help = 'Creates dummy mentors with predefined skills'

    def add_arguments(self, parser):
        parser.add_argument('total', type=int,
                            help='Number of mentors to create')

    @transaction.atomic
    def handle(self, *args, **kwargs):
        total = kwargs['total']

        skills = []
        for skill_name in SKILLS:
            skill, created = Skill.objects.get_or_create(
                title=skill_name,
                defaults={
                    'name': skill_name.lower().replace(' ', '_'),
                    'description': f"Expert knowledge in {skill_name}"
                }
            )
            skills.append(skill)

        self.stdout.write(self.style.SUCCESS('Skills created successfully'))

        # Create mentors
        for i in range(total):
            try:
                # Create user
                username = fake.user_name()
                while User.objects.filter(username=username).exists():
                    username = fake.user_name()

                user = User.objects.create_user(
                    username=username,
                    email=fake.email(),
                    password='testpass123'
                )
                user.first_name = fake.first_name()
                user.last_name = fake.last_name()
                user.save()

                # Create mentor profile
                mentor = Mentor.objects.create(
                    user=user,
                    bio=fake.paragraph(nb_sentences=3),
                    rating=round(random.uniform(3.5, 5.0), 2),
                    is_available=random.choice([True, False]),
                    experience_level=random.choice(EXPERIENCE_LEVELS),
                    hourly_rate=random.randint(30, 150)
                )

                # Assign 2-4 random skills to each mentor
                num_skills = random.randint(2, 4)
                selected_skills = random.sample(skills, num_skills)
                mentor.skills.set(selected_skills)

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created mentor: {user.get_full_name()} with skills: {", ".join([s.title for s in selected_skills])}'
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'Failed to create mentor {i+1}: {str(e)}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {total} dummy mentors')
        )
