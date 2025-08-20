from django.db import models
from django.utils.translation import gettext_lazy as _


class PaintPrice(models.Model):
    name = models.CharField(max_length=100, verbose_name=_("Naziv"))
    price_per_m2 = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name=_("Cijena po m2")
    )
    currency = models.CharField(max_length=10, default="EUR", verbose_name=_("Valuta"))

    class Meta:
        verbose_name = _("Cjenik farbanja")
        verbose_name_plural = _("Cjenici farbanja")
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.price_per_m2} {self.currency}/m2)"
