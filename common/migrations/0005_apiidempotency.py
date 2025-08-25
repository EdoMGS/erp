from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("common", "0004_alter_audittrail_options_and_more"),
        ("tenants", "0006_tenantuser"),
    ]

    operations = [
        migrations.CreateModel(
            name="ApiIdempotency",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True, primary_key=True, serialize=False, verbose_name="ID"
                    ),
                ),
                ("path", models.CharField(max_length=255)),
                ("method", models.CharField(max_length=10)),
                ("key", models.CharField(max_length=255)),
                ("request_hash", models.CharField(blank=True, max_length=64, null=True)),
                ("status_code", models.PositiveIntegerField(default=200)),
                ("response_body", models.JSONField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tenants.tenant"
                    ),
                ),
            ],
            options={
                "indexes": [
                    models.Index(
                        fields=["tenant", "path", "method", "key"], name="api_idem_tpmk_idx"
                    ),
                ],
                "unique_together": {("tenant", "path", "method", "key")},
            },
        )
    ]
