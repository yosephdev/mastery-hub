from django.core.management.base import BaseCommand
from masteryhub.models import Category

class Command(BaseCommand):
    help = 'Creates default forum categories if they do not exist'

    def handle(self, *args, **kwargs):
        default_categories = [
            'General Discussion',
            'Technical Support',
            'Learning Resources',
            'Project Showcase',
            'Career Advice',
            'Community Events',
            'Feedback & Suggestions',
            'Off-topic'
        ]

        for category_name in default_categories:
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'description': f'Forum category for {category_name.lower()}'}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'Category already exists: {category_name}')) 