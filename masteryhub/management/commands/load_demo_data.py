from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from profiles.models import Profile
from masteryhub.models import Mentor, Skill, Category
from decimal import Decimal


class Command(BaseCommand):
    help = 'Loads initial demo data for testing'

    def handle(self, *args, **kwargs):
        try:           
            categories = {
                'Programming': 'Learn various programming languages',
                'Web Development': 'Build websites and web applications',
                'Data Science': 'Analyze data and build models',
                'Design': 'Create beautiful user interfaces',
            }

            for name, description in categories.items():
                Category.objects.get_or_create(
                    name=name,
                    defaults={'description': description}
                )
           
            skills_data = [
                ('Python', 'Programming'),
                ('JavaScript', 'Web Development'),
                ('HTML/CSS', 'Web Development'),
                ('Data Analysis', 'Data Science'),
                ('UI Design', 'Design'),
            ]

            for skill_name, category_name in skills_data:
                category = Category.objects.get(name=category_name)
                Skill.objects.get_or_create(
                    title=skill_name,
                    defaults={
                        'name': skill_name.lower().replace(' ', '_'),
                        'description': f'Skills in {skill_name}',
                        'category': category
                    }
                )

            self.stdout.write(
                self.style.SUCCESS('Successfully loaded initial demo data')
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error loading demo data: {str(e)}')
            )
