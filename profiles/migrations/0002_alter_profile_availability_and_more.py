# Generated by Django 5.1.4 on 2025-02-11 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("profiles", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="profile",
            name="availability",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="profile",
            name="github_profile",
            field=models.URLField(default=""),
        ),
        migrations.AlterField(
            model_name="profile",
            name="linkedin_profile",
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="profile",
            name="mentorship_areas",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AlterField(
            model_name="profile",
            name="preferred_mentoring_method",
            field=models.CharField(blank=True, default="One-on-one", max_length=100),
        ),
    ]
