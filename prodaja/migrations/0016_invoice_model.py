from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from decimal import Decimal


class Migration(migrations.Migration):
    dependencies = [
        ("tenants", "0005_tenant_vat_fiscal_and_settings_accounts"),
        ("prodaja", "0015_work_order_models"),
    ]

    operations = [
        migrations.CreateModel(
            name="Invoice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created at")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated at")),
                ("is_active", models.BooleanField(default=True, verbose_name="Active")),
                (
                    "number",
                    models.CharField(
                        max_length=20,
                        help_text="Formatted as NNN-OO-UU",
                    ),
                ),
                ("issued_at", models.DateTimeField()),
                ("operator_mark", models.CharField(max_length=16)),
                (
                    "net_amount",
                    models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12),
                ),
                (
                    "vat_amount",
                    models.DecimalField(decimal_places=2, default=Decimal("0.00"), max_digits=12),
                ),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="invoice_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="invoice_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tenants.tenant"
                    ),
                ),
            ],
            options={"ordering": ["-created_at"], "unique_together": {("tenant", "number")}},
        ),
    ]
