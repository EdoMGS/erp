from __future__ import annotations

from django.db import models
from django.utils import timezone


class TaxLocalRate(models.Model):
    """Lokalne JLS stope poreza na dohodak (lower/higher) s periodom važenja.
    Primjena: prema prebivalištu zaposlenika i datumu isplate.
    """
    id = models.BigAutoField(primary_key=True)
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.PROTECT, related_name="tax_local_rates")
    jls_code = models.CharField(max_length=20, help_text="RIJEKA, BAKAR, KRALJEVICA, ZAGREB, DEFAULT ...")
    name = models.CharField(max_length=120)
    lower_rate = models.DecimalField(max_digits=5, decimal_places=2)
    higher_rate = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateField(default=timezone.now)
    valid_to = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        db_table = "tax_local_rate"
        indexes = [models.Index(fields=["tenant", "jls_code", "valid_from"])]
        unique_together = ("tenant", "jls_code", "valid_from")
        ordering = ("jls_code", "-valid_from")

    def __str__(self):  # pragma: no cover
        vf = self.valid_from.isoformat()
        vt = self.valid_to.isoformat() if self.valid_to else "∞"
        return f"{self.jls_code} {self.lower_rate}/{self.higher_rate} {vf}→{vt}"
