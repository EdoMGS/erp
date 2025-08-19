from decimal import Decimal

from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    # Allow null/blank so tests creating multiple tenants without domain don't violate unique constraint
    domain = models.CharField(max_length=255, unique=True, null=True, blank=True, verbose_name="Domain")

    # Compliance / VAT setup
    vat_registered = models.BooleanField(default=True)
    default_vat_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("25.00"))

    # Fiscalization (fiskalizacija) related defaults (HR specific)
    fiscal_cert_path = models.CharField(
        max_length=255, blank=True, help_text="Path to .p12 or keystore for fiskalizacija"
    )
    premise_code = models.CharField(max_length=10, blank=True, help_text="Oznaka poslovnog prostora")
    device_code = models.CharField(max_length=10, blank=True, help_text="Oznaka naplatnog uređaja")
    default_operator_mark = models.CharField(max_length=10, blank=True, help_text="Default oznaka operatera")

    def __str__(self):
        return self.name


class TenantSettings(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name="settings")
    ramp_up_min_net = models.DecimalField(max_digits=10, decimal_places=2, default=800.00)

    # Existing (legacy minimal) accounts
    acc_expense_ops = models.CharField(max_length=20, default="4000")
    acc_expense_payroll = models.CharField(max_length=20, default="4100")
    acc_equity_profit = models.CharField(max_length=20, default="5000")
    acc_ar_customers = models.CharField(max_length=20, default="1200")

    # New: profit-share / VAT / rounding specific accounts (configurable, no hard-coding)
    acc_profit_share_expense = models.CharField(max_length=20, default="7600")  # DR 76x
    acc_profit_share_liability = models.CharField(max_length=20, default="2600")  # CR 26x
    acc_profit_share_equity = models.CharField(max_length=20, default="8400")  # CR 84x (retained earnings)
    acc_rounding_diff = models.CharField(max_length=20, default="4999")  # Rounding differences bucket
    acc_vat_output = models.CharField(max_length=20, default="4700")  # PDV izlazni
    acc_revenue_services = models.CharField(max_length=20, default="4000")  # Prihodi usluga

    def __str__(self):
        return f"Settings for {self.tenant.name}"
