from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from tenants.models import Tenant


class BreakEvenSnapshot(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name=_("Tenant"))
    division = models.CharField(max_length=64, verbose_name=_("Divizija"))
    date = models.DateField(verbose_name=_("Datum"))
    fixed_costs = models.DecimalField(max_digits=14, decimal_places=2, verbose_name=_("Fiksni troškovi"))
    revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Prihod"),
    )
    profit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Profit"),
    )
    break_even_qty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Break-even količina"),
    )
    status = models.CharField(max_length=16, default="red", verbose_name=_("Status"))  # red/green

    class Meta:
        unique_together = ("tenant", "division", "date")
        verbose_name = _("Break-even snimka")
        verbose_name_plural = _("Break-even snimke")

    def __str__(self):
        return f"{self.tenant} - {self.division} ({self.date})"
