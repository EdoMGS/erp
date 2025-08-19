from decimal import Decimal

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("tenants", "0004_merge_0003_alter_tenant_domain_0003_tenantsettings"),
    ]

    operations = [
        migrations.AddField(
            model_name="tenant",
            name="vat_registered",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="tenant",
            name="default_vat_rate",
            field=models.DecimalField(default=Decimal("25.00"), max_digits=5, decimal_places=2),
        ),
        migrations.AddField(
            model_name="tenant",
            name="fiscal_cert_path",
            field=models.CharField(blank=True, max_length=255, help_text="Path to .p12 or keystore for fiskalizacija"),
        ),
        migrations.AddField(
            model_name="tenant",
            name="premise_code",
            field=models.CharField(blank=True, max_length=10, help_text="Oznaka poslovnog prostora"),
        ),
        migrations.AddField(
            model_name="tenant",
            name="device_code",
            field=models.CharField(blank=True, max_length=10, help_text="Oznaka naplatnog uređaja"),
        ),
        migrations.AddField(
            model_name="tenant",
            name="default_operator_mark",
            field=models.CharField(blank=True, max_length=10, help_text="Default oznaka operatera"),
        ),
        migrations.AddField(
            model_name="tenantsettings",
            name="acc_profit_share_expense",
            field=models.CharField(default="7600", max_length=20),
        ),
        migrations.AddField(
            model_name="tenantsettings",
            name="acc_profit_share_liability",
            field=models.CharField(default="2600", max_length=20),
        ),
        migrations.AddField(
            model_name="tenantsettings",
            name="acc_profit_share_equity",
            field=models.CharField(default="8400", max_length=20),
        ),
        migrations.AddField(
            model_name="tenantsettings",
            name="acc_rounding_diff",
            field=models.CharField(default="4999", max_length=20),
        ),
        migrations.AddField(
            model_name="tenantsettings",
            name="acc_vat_output",
            field=models.CharField(default="4700", max_length=20),
        ),
        migrations.AddField(
            model_name="tenantsettings",
            name="acc_revenue_services",
            field=models.CharField(default="4000", max_length=20),
        ),
    ]
