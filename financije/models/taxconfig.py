from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TaxConfiguration(models.Model):
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="tax_configurations",
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=100, verbose_name=_("Naziv konfiguracije poreza"))
    # Osnovni postotak poreza (rate) s validacijom između 0 i 100%
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name=_("Stopa poreza (%)"),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    # Polja za period važenja konfiguracije
    valid_from = models.DateField(verbose_name=_("Vrijedi od"))
    valid_to = models.DateField(null=True, blank=True, verbose_name=_("Vrijedi do"))
    # Status konfiguracije – ako je aktivna, druge se deaktiviraju
    is_active = models.BooleanField(default=True, verbose_name=_("Aktivna konfiguracija"))

    # Dodatna polja za obračun različitih aspekata poreza
    mirovinsko_1 = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0.15"),
        verbose_name=_("Mirovinsko 1"),
    )
    mirovinsko_2 = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0.05"),
        verbose_name=_("Mirovinsko 2"),
    )
    zdravstveno = models.DecimalField(
        max_digits=5,
        decimal_places=3,
        default=Decimal("0.165"),
        verbose_name=_("Zdravstveno"),
    )
    niza_stopa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0.20"),
        verbose_name=_("Niža stopa poreza"),
    )
    visa_stopa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0.30"),
        verbose_name=_("Viša stopa poreza"),
    )
    osobni_odbitak = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("560.00"),
        verbose_name=_("Osobni odbitak"),
    )
    prirez = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal("0.50"),
        verbose_name=_("Prirez"),
    )
    granica_visa_stopa = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("1800.00"),
        verbose_name=_("Granica za višu stopu poreza"),
    )
    minimal_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("780.00"),
        verbose_name=_("Minimalna plaća (€)"),
    )
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis konfiguracije"))

    class Meta:
        verbose_name = _("Tax Configuration")
        verbose_name_plural = _("Tax Configurations")
        constraints = [
            models.CheckConstraint(
                check=models.Q(tax_rate__gte=0) & models.Q(tax_rate__lte=100),
                name="valid_tax_rate",
            )
        ]
        indexes = [
            models.Index(fields=["valid_from", "valid_to"]),
            models.Index(fields=["is_active"]),
        ]

    def save(self, *args, **kwargs):
        from django.db import transaction

        with transaction.atomic():
            if self.is_active:
                # Deaktiviraj sve ostale aktivne konfiguracije
                TaxConfiguration.objects.filter(is_active=True).exclude(pk=self.pk).update(
                    is_active=False
                )
            super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Municipality(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Naziv općine"))
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Stopa prireza (%)"),
    )

    class Meta:
        verbose_name = _("Općina")
        verbose_name_plural = _("Općine")

    def __str__(self):
        return self.name
