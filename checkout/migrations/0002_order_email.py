# Generated by Django 5.0.6 on 2024-08-04 23:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("checkout", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="email",
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
    ]
