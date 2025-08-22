from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("tenants", "0005_tenant_vat_fiscal_and_settings_accounts"),
        ("prodaja", "0013_remove_projectservicetype_tenant_id_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="Quote",
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
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="quote_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="quote_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("number", models.CharField(max_length=64)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("draft", "draft"),
                            ("sent", "sent"),
                            ("accepted", "accepted"),
                            ("expired", "expired"),
                        ],
                        default="draft",
                        max_length=20,
                    ),
                ),
                ("valid_until", models.DateField(blank=True, null=True)),
                ("currency", models.CharField(max_length=3)),
                ("vat_rate", models.DecimalField(decimal_places=2, max_digits=5)),
                ("is_vat_registered", models.BooleanField(default=True)),
                ("customer_name", models.CharField(max_length=255)),
                ("customer_vat_id", models.CharField(blank=True, max_length=64, null=True)),
                ("site_address", models.CharField(blank=True, max_length=255, null=True)),
                ("contact_email", models.EmailField(blank=True, max_length=254, null=True)),
                ("contact_phone", models.CharField(blank=True, max_length=64, null=True)),
                ("lead_source", models.CharField(blank=True, max_length=64, null=True)),
                ("risk_band", models.CharField(max_length=10)),
                ("contingency_pct", models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                (
                    "margin_target_pct",
                    models.DecimalField(decimal_places=2, default=0, max_digits=5),
                ),
                ("accepted_at", models.DateTimeField(blank=True, null=True)),
                ("accepted_by", models.CharField(blank=True, max_length=255, null=True)),
                ("acceptance_hash", models.CharField(blank=True, max_length=128, null=True)),
                ("warranty", models.CharField(blank=True, max_length=255, null=True)),
                ("payment_terms", models.CharField(blank=True, max_length=255, null=True)),
                ("revision", models.PositiveIntegerField(default=1)),
                ("attachments", models.JSONField(blank=True, default=list)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="QuoteItem",
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
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="quoteitem_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="quoteitem_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("type", models.CharField(max_length=32)),
                ("description", models.TextField(blank=True)),
                ("uom_base", models.CharField(max_length=16)),
                ("qty_base", models.DecimalField(decimal_places=2, max_digits=10)),
                ("item_ref", models.CharField(blank=True, max_length=64, null=True)),
                ("paint_system_id", models.CharField(blank=True, max_length=64, null=True)),
                (
                    "quote",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="items",
                        to="prodaja.quote",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="QuoteOption",
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
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="quoteoption_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="quoteoption_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("name", models.CharField(max_length=32)),
                (
                    "quote",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="options",
                        to="prodaja.quote",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="EstimSnapshot",
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
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="estimsnapshot_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="estimsnapshot_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("norms_version", models.CharField(max_length=32)),
                ("price_list_version", models.CharField(max_length=32)),
                ("rounding_policy", models.CharField(max_length=16)),
                ("input_data", models.JSONField()),
                ("breakdown", models.JSONField()),
                ("version", models.CharField(max_length=32)),
                (
                    "option",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="snapshots",
                        to="prodaja.quoteoption",
                    ),
                ),
                (
                    "quote",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="snapshots",
                        to="prodaja.quote",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="QuoteRevision",
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
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="quoterevision_created",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "updated_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="quoterevision_updated",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("reason_code", models.CharField(max_length=32)),
                ("delta", models.JSONField(blank=True, default=dict)),
                (
                    "new_snapshot",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="new_revisions",
                        to="prodaja.estimsnapshot",
                    ),
                ),
                (
                    "parent",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="revisions",
                        to="prodaja.quote",
                    ),
                ),
                (
                    "prev_snapshot",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="prev_revisions",
                        to="prodaja.estimsnapshot",
                    ),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="tenants.tenant",
                    ),
                ),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]
