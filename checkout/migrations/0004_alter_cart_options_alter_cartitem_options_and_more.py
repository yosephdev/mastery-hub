# Generated by Django 5.1.3 on 2024-12-06 14:26

import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("checkout", "0003_remove_cart_sessions_alter_cartitem_unique_together"),
        ("masteryhub", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="cart",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterModelOptions(
            name="cartitem",
            options={"ordering": ["created_at"]},
        ),
        migrations.AddField(
            model_name="cart",
            name="is_active",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="cart",
            name="last_activity",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="cart",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name="cartitem",
            name="created_at",
            field=models.DateTimeField(
                auto_now_add=True, default=django.utils.timezone.now
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="cartitem",
            name="price_at_time_of_adding",
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name="cartitem",
            name="updated_at",
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddIndex(
            model_name="cart",
            index=models.Index(
                fields=["user", "is_active"], name="checkout_ca_user_id_627a7b_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="cartitem",
            index=models.Index(
                fields=["cart", "session"], name="checkout_ca_cart_id_1c7341_idx"
            ),
        ),
    ]