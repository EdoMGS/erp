from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ("tenants", "0005_tenant_vat_fiscal_and_settings_accounts"),
        ("financije", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="TaxLocalRate",
            fields=[
                ("id", models.BigAutoField(primary_key=True, serialize=False)),
                (
                    "tenant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="tax_local_rates",
                        to="tenants.tenant",
                    ),
                ),
                ("jls_code", models.CharField(max_length=20)),
                ("name", models.CharField(max_length=120)),
                ("lower_rate", models.DecimalField(decimal_places=2, max_digits=5)),
                ("higher_rate", models.DecimalField(decimal_places=2, max_digits=5)),
                ("valid_from", models.DateField(default=django.utils.timezone.now)),
                ("valid_to", models.DateField(blank=True, null=True)),
                ("active", models.BooleanField(default=True)),
            ],
            options={
                "db_table": "tax_local_rate",
                "ordering": ("jls_code", "-valid_from"),
                "unique_together": {("tenant", "jls_code", "valid_from")},
            },
        ),
        migrations.AddIndex(
            model_name="taxlocalrate",
            index=models.Index(fields=["tenant", "jls_code", "valid_from"], name="tax_jls_vf_idx"),
        ),
    ]
