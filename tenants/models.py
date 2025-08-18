from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    # Allow null/blank so tests creating multiple tenants without domain don't violate unique constraint
    domain = models.CharField(max_length=255, unique=True, null=True, blank=True, verbose_name="Domain")

    def __str__(self):
        return self.name


class TenantSettings(models.Model):
    tenant = models.OneToOneField(Tenant, on_delete=models.CASCADE, related_name="settings")
    ramp_up_min_net = models.DecimalField(max_digits=10, decimal_places=2, default=800.00)
    acc_expense_ops = models.CharField(max_length=20, default="4000")
    acc_expense_payroll = models.CharField(max_length=20, default="4100")
    acc_equity_profit = models.CharField(max_length=20, default="5000")
    acc_ar_customers = models.CharField(max_length=20, default="1200")

    def __str__(self):
        return f"Settings for {self.tenant.name}"
