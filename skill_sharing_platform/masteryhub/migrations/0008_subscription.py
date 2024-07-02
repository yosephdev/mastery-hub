# Generated by Django 5.0.6 on 2024-07-01 12:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("masteryhub", "0007_review"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "plan",
                    models.CharField(
                        choices=[
                            ("free", "Free"),
                            ("basic", "Basic"),
                            ("premium", "Premium"),
                        ],
                        default="free",
                        max_length=20,
                    ),
                ),
                ("start_date", models.DateField(auto_now_add=True)),
                ("end_date", models.DateField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]