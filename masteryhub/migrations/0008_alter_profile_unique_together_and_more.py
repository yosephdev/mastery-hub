# Generated by Django 5.0.6 on 2024-07-23 06:53

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("masteryhub", "0007_auto_20240722_0943"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name="profile",
            unique_together={("user",)},
        ),
        migrations.AddIndex(
            model_name="profile",
            index=models.Index(fields=["user"], name="masteryhub__user_id_bae410_idx"),
        ),
    ]