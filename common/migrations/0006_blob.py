from django.db import migrations, models
import django.utils.timezone
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("tenants", "0006_tenantuser"),
        ("common", "0005_apiidempotency"),
    ]

    operations = [
        migrations.CreateModel(
            name="Blob",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                (
                    "kind",
                    models.CharField(
                        max_length=32,
                        choices=[
                            ("invoice_pdf", "Invoice PDF"),
                            ("invoice_ubl", "Invoice UBL"),
                            ("joppd_xml", "JOPPD XML"),
                            ("other", "Other"),
                        ],
                    ),
                ),
                ("key", models.CharField(max_length=256)),
                ("sha256", models.CharField(max_length=64, db_index=True)),
                ("size", models.BigIntegerField()),
                ("mimetype", models.CharField(max_length=128)),
                ("uri", models.CharField(max_length=512)),
                (
                    "created_at",
                    models.DateTimeField(default=django.utils.timezone.now, db_index=True),
                ),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tenants.tenant"
                    ),
                ),
            ],
            options={
                "unique_together": {("tenant", "kind", "key")},
            },
        ),
    ]
