from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from tenants.models import Tenant


class FixedCost(models.Model):
    PERIOD_CHOICES = [
        ("M", "Mjesečno"),
        ("Q", "Kvartalno"),
        ("Y", "Godišnje"),
    ]
    division = models.CharField(max_length=64, verbose_name=_("Divizija"))
    name = models.CharField(max_length=128, verbose_name=_("Naziv troška"))
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Iznos"))
    period = models.CharField(max_length=1, choices=PERIOD_CHOICES, default="M", verbose_name=_("Period"))
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name=_("Tenant"))

    def monthly_value(self):
        if self.period == "M":
            return self.amount
        elif self.period == "Q":
            return self.amount / Decimal("3.00")
        elif self.period == "Y":
            return self.amount / Decimal("12.00")
        return self.amount

    def __str__(self):
        return f"{self.division} - {self.name} ({self.get_period_display()})"


class VariableCostPreset(models.Model):
    division = models.CharField(max_length=64, verbose_name=_("Divizija"))
    name = models.CharField(max_length=128, verbose_name=_("Naziv"))
    amount_per_unit = models.DecimalField(max_digits=12, decimal_places=4, verbose_name=_("Iznos po jedinici"))
    unit = models.CharField(max_length=32, verbose_name=_("Jedinica"))
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name=_("Tenant"))

    def __str__(self):
        return f"{self.division} - {self.name} ({self.unit})"
