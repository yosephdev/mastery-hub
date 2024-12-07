from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from profiles.models import Profile


class Command(BaseCommand):
    help = 'Loads demo data for mentors'

    def handle(self, *args, **kwargs):
        # Demo data
        demo_mentors = [
            {
                'username': 'sarah_tech',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'email': 'sarah@example.com',
                'profile': {
                    'bio': 'Senior Software Engineer with 8 years of experience in full-stack development. Passionate about mentoring new developers and sharing knowledge in web technologies.',
                    'is_expert': True,
                    'expertise_areas': 'Python, Django, JavaScript, React',
                    'years_of_experience': 8,
                    'hourly_rate': 75.00,
                    'availability': 'Evenings and weekends',
                    'linkedin_url': 'https://linkedin.com/in/sarah-tech',
                    'github_url': 'https://github.com/sarah-tech',
                    'website_url': 'https://sarah-tech.dev'
                }
            },
            {
                'username': 'mike_data',
                'first_name': 'Michael',
                'last_name': 'Chen',
                'email': 'mike@example.com',
                'profile': {
                    'bio': 'Data Scientist with expertise in machine learning and AI. Love helping others understand complex data concepts and build practical ML solutions.',
                    'is_expert': True,
                    'expertise_areas': 'Python, Machine Learning, Data Analysis, SQL',
                    'years_of_experience': 6,
                    'hourly_rate': 85.00,
                    'availability': 'Weekday afternoons',
                    'linkedin_url': 'https://linkedin.com/in/mike-data',
                    'github_url': 'https://github.com/mike-data',
                    'website_url': 'https://mike-data.ai'
                }
            },
            {
                'username': 'anna_design',
                'first_name': 'Anna',
                'last_name': 'Martinez',
                'email': 'anna@example.com',
                'profile': {
                    'bio': 'UX/UI Designer with a background in psychology. Specialized in creating user-centered designs and teaching design thinking principles.',
                    'is_expert': True,
                    'expertise_areas': 'UI/UX Design, Figma, Adobe XD, User Research',
                    'years_of_experience': 5,
                    'hourly_rate': 65.00,
                    'availability': 'Flexible schedule',
                    'linkedin_url': 'https://linkedin.com/in/anna-design',
                    'github_url': '',
                    'website_url': 'https://anna-design.com'
                }
            }
        ]

        for mentor_data in demo_mentors:
            profile_data = mentor_data.pop('profile')

            user, created = User.objects.get_or_create(
                username=mentor_data['username'],
                defaults={
                    **mentor_data,
                    'password': make_password('demo123456'),
                    'is_active': True
                }
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"Created user: {user.username}")
                )

            # Create or update profile
            profile, created = Profile.objects.get_or_create(
                user=user,
                defaults=profile_data
            )

            if not created:
                # Update existing profile
                for key, value in profile_data.items():
                    setattr(profile, key, value)
                profile.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"{'Created' if created else 'Updated'} profile for: {user.username}"
                )
            )

        self.stdout.write(self.style.SUCCESS('Successfully loaded demo data'))
