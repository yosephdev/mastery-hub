# Generated by Django 5.0.6 on 2024-08-05 07:25

import django_countries.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("checkout", "0002_order_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="country",
            field=django_countries.fields.CountryField(max_length=40),
        ),
    ]
