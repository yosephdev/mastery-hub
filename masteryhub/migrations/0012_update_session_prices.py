# Generated by Django 5.1.3 on 2025-03-13 13:47

from django.db import migrations
from decimal import Decimal


def update_session_prices(apps, schema_editor):
    Session = apps.get_model('masteryhub', 'Session')
    for session in Session.objects.all():
        if not session.price:
            session.price = Decimal('99.99')
            session.save()


def reverse_session_prices(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('masteryhub', '0011_mentor_is_demo'),
    ]

    operations = [
        migrations.RunPython(update_session_prices, reverse_session_prices),
    ]
