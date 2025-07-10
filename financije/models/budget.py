from decimal import Decimal

from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _


class Budget(models.Model):
    godina = models.PositiveIntegerField(verbose_name=_("Godina"))
    mjesec = models.PositiveIntegerField(verbose_name=_("Mjesec"))
    predvidjeni_prihod = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Predviđeni prihod (€)")
    )
    predvidjeni_trosak = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Predviđeni trošak (€)")
    )
    stvarni_prihod = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("Stvarni prihod (€)")
    )
    stvarni_trosak = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name=_("Stvarni trošak (€)")
    )

    class Meta:
        unique_together = ('godina', 'mjesec')
        verbose_name = _("Proračun")
        verbose_name_plural = _("Proračuni")
        constraints = [
            models.CheckConstraint(
                check=Q(mjesec__gte=1) & Q(mjesec__lte=12),
                name="valid_month_check"
            )
        ]

    def __str__(self):
        return f"Budget {self.mjesec}/{self.godina}"
