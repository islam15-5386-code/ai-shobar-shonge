from decimal import Decimal

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("businesses", "0002_business_onboarding_fields"),
        ("marketplace", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="MarketplaceSetting",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("default_commission_rate", models.DecimalField(decimal_places=2, default=Decimal("10.00"), max_digits=6)),
                ("auto_approve_vendors", models.BooleanField(default=False)),
                ("auto_approve_products", models.BooleanField(default=False)),
                ("vendor_self_signup_enabled", models.BooleanField(default=False)),
                ("require_vendor_kyc", models.BooleanField(default=False)),
                ("min_payout_amount", models.DecimalField(decimal_places=2, default=Decimal("1000.00"), max_digits=12)),
                ("default_payout_method", models.CharField(default="bank", max_length=80)),
                ("default_return_policy", models.TextField(blank=True)),
                ("default_delivery_policy", models.TextField(blank=True)),
                ("support_email", models.EmailField(blank=True, max_length=254)),
                ("support_phone", models.CharField(blank=True, max_length=40)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "business",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="marketplace_settings",
                        to="businesses.business",
                    ),
                ),
            ],
        ),
    ]

