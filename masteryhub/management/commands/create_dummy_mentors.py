from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from profiles.models import Profile
from masteryhub.models import Mentor, Skill, Category
from decimal import Decimal
import random

# Additional skills to add
ADDITIONAL_SKILLS = [
    ("AWS Cloud Services", "web_dev"),
    ("Azure Cloud Computing", "web_dev"),
    ("Blockchain Development", "programming"),
    ("Computer Vision", "data_science"),
    ("Cybersecurity Fundamentals", "programming"),
    ("Digital Marketing", "web_dev"),
    ("Ethical Hacking", "programming"),
    ("Graphic Design", "web_dev"),
    ("IoT Development", "programming"),
    ("Podcast Production", "web_dev"),
    ("Video Production", "web_dev")
]

class Command(BaseCommand):
    help = 'Creates dummy mentors with predefined skills'

    def handle(self, *args, **kwargs):
        try:
            # Create categories
            categories = {}
            category_data = [
                ('Programming', 'programming', 'Programming and Development'),
                ('Web Development', 'web_dev', 'Web Development Skills'),
                ('Data Science', 'data_science', 'Data Science and Analytics')
            ]
            
            for name, key, description in category_data:
                category, _ = Category.objects.get_or_create(name=name, defaults={'description': description})
                categories[key] = category
                self.stdout.write(self.style.SUCCESS(f'Created category: {name}'))

            # Define skills with their categories
            skills_data = [
                ('Python', 'programming', 'Expertise in Python programming language'),
                ('Django', 'web_dev', 'Web development with Django framework'),
                ('JavaScript', 'web_dev', 'Frontend and backend JavaScript development'),
                ('React', 'web_dev', 'Frontend development with React'),
                ('Machine Learning', 'data_science', 'Machine Learning and AI development'),
                ('Data Analysis', 'data_science', 'Data analysis and visualization'),
                ('SQL', 'data_science', 'Database management and SQL queries')
            ]

            # Add additional skills
            for skill_name, category_key in ADDITIONAL_SKILLS:
                skills_data.append((skill_name, category_key, f'Expertise in {skill_name}'))

            # Create skills
            skills_map = {}
            for title, category_key, description in skills_data:
                category = categories[category_key]
                skill, _ = Skill.objects.get_or_create(
                    title=title,
                    defaults={
                        'name': title.lower().replace(' ', '_'),
                        'description': description,
                        'category': category
                    }
                )
                skills_map[title] = skill
                self.stdout.write(self.style.SUCCESS(f"Created skill: {title}"))

            # Define mentors
            demo_mentors = [
                {"username": "sarah_tech", "first_name": "Sarah", "last_name": "Johnson", "email": "sarah@example.com",
                 "bio": "Senior Software Engineer with 8 years of experience.", "experience": 8, "hourly_rate": 75.00,
                 "availability": "Evenings and weekends", "skills": ["Python", "Django", "JavaScript"]},
                {"username": "david_data", "first_name": "David", "last_name": "Chen", "email": "david@example.com",
                 "bio": "Data Scientist specializing in Machine Learning and Analytics.", "experience": 6, "hourly_rate": 85.00,
                 "availability": "Weekday afternoons", "skills": ["Python", "Machine Learning", "Data Analysis"]},
                {"username": "maria_web", "first_name": "Maria", "last_name": "Garcia", "email": "maria@example.com",
                 "bio": "Frontend Developer passionate about creating beautiful user experiences.", "experience": 5, "hourly_rate": 65.00,
                 "availability": "Flexible schedule", "skills": ["JavaScript", "React"]},
            ]

            # Create mentors
            for mentor_data in demo_mentors:
                user, created = User.objects.get_or_create(
                    username=mentor_data['username'],
                    defaults={
                        'first_name': mentor_data['first_name'],
                        'last_name': mentor_data['last_name'],
                        'email': mentor_data['email'],
                        'password': make_password('password123')
                    }
                )

                if created:
                    profile = Profile.objects.create(
                        user=user,
                        bio=mentor_data['bio'],
                        is_expert=True,
                        mentorship_areas=', '.join(mentor_data['skills']),
                        years_of_experience=mentor_data['experience'],
                        hourly_rate=mentor_data['hourly_rate'],
                        availability=mentor_data['availability']
                    )

                    mentor = Mentor.objects.create(
                        user=user,
                        experience_level='expert' if mentor_data['experience'] > 5 else 'intermediate',
                        rating=random.uniform(4.5, 5.0),
                        is_available=True,
                        hourly_rate=Decimal(str(mentor_data['hourly_rate']))
                    )
                    
                    mentor.skills.add(*[skills_map[skill] for skill in mentor_data['skills']])
                    self.stdout.write(self.style.SUCCESS(f"Created mentor: {mentor_data['first_name']} {mentor_data['last_name']}"))
                else:
                    self.stdout.write(self.style.WARNING(f"User {mentor_data['username']} already exists."))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error: {str(e)}"))
