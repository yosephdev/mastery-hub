# Generated by Django 5.0.6 on 2024-07-13 12:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("masteryhub", "0014_mentorship_created_at_mentorship_status_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="dummy_field",
            field=models.BooleanField(default=False),
        ),
    ]