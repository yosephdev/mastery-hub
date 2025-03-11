from django.core.management.base import BaseCommand
from masteryhub.models import Skill, Category

class Command(BaseCommand):
    help = 'Loads initial categories and skills for the platform'

    def handle(self, *args, **kwargs):
        try:
            # Define categories
            category_data = {
                'programming': {'name': 'Programming', 'description': 'Learn various programming languages'},
                'web_dev': {'name': 'Web Development', 'description': 'Build websites and web applications'},
                'data_science': {'name': 'Data Science', 'description': 'Analyze data and build models'},
                'design': {'name': 'Design', 'description': 'Create beautiful user interfaces'},
                'cloud_computing': {'name': 'Cloud Computing', 'description': 'Learn AWS, Azure, and cloud security'},
                'cybersecurity': {'name': 'Cybersecurity', 'description': 'Protect networks and systems from attacks'},
            }

            categories = {}
            for key, data in category_data.items():
                category, created = Category.objects.get_or_create(
                    name=data['name'], defaults={'description': data['description']}
                )
                categories[key] = category
                if created:
                    self.stdout.write(self.style.SUCCESS(f"Category created: {data['name']}"))
                else:
                    self.stdout.write(self.style.WARNING(f"Category already exists: {data['name']}"))

            # Define skills
            skills_data = [
                ('Python', 'programming'),
                ('JavaScript', 'web_dev'),
                ('HTML/CSS', 'web_dev'),
                ('Django', 'web_dev'),
                ('React', 'web_dev'),
                ('Machine Learning', 'data_science'),
                ('Data Analysis', 'data_science'),
                ('SQL', 'data_science'),
                ('UI/UX Design', 'design'),
                ('Cloud Security', 'cybersecurity'),
                ('AWS Cloud', 'cloud_computing'),
                ('Azure Cloud', 'cloud_computing'),
                ('Penetration Testing', 'cybersecurity'),
            ]

            for skill_name, category_key in skills_data:
                if category_key in categories:
                    skill, created = Skill.objects.get_or_create(
                        title=skill_name,
                        defaults={
                            'name': skill_name.lower().replace(' ', '_'),
                            'description': f'Expertise in {skill_name}',
                            'category': categories[category_key]
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Skill created: {skill_name} in {categories[category_key].name}"))
                    else:
                        self.stdout.write(self.style.WARNING(f"Skill already exists: {skill_name}"))
                else:
                    self.stdout.write(self.style.ERROR(f"Invalid category for skill '{skill_name}': {category_key}"))

            self.stdout.write(self.style.SUCCESS('Successfully loaded initial data! 🚀'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading demo data: {str(e)}'))
