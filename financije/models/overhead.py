from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _


class OverheadManager(models.Manager):
    def get_by_year_month(self, godina, mjesec):
        return self.get_or_none(godina=godina, mjesec=mjesec)

    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None


class Overhead(models.Model):
    godina = models.PositiveIntegerField(verbose_name=_("Godina"))
    mjesec = models.PositiveIntegerField(verbose_name=_("Mjesec"))
    overhead_ukupno = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Ukupni overhead (€)")
    )
    mjesecni_kapacitet_sati = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("1600.00"),
        verbose_name=_("Mjesečni kapacitet sati"),
    )

    objects = OverheadManager()

    class Meta:
        unique_together = ("godina", "mjesec")
        verbose_name = _("Overhead")
        verbose_name_plural = _("Overheadi")
        indexes = [models.Index(fields=["godina", "mjesec"])]

    def __str__(self):
        return f"Overhead {self.mjesec}/{self.godina}: {self.overhead_ukupno} €"

    def distribute_to_projects(self):
        from financije.services import distribute_overhead_by_project

        distribute_overhead_by_project(self.godina, self.mjesec)


class OverheadCategory(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Category Name"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Category Description"))

    class Meta:
        verbose_name = _("Overhead Category")
        verbose_name_plural = _("Overhead Categories")

    def __str__(self):
        return self.name


class MonthlyOverhead(models.Model):
    year = models.PositiveIntegerField(verbose_name=_("Year"))
    month = models.PositiveIntegerField(verbose_name=_("Month"))
    category = models.ForeignKey(
        OverheadCategory, on_delete=models.CASCADE, verbose_name=_("Category")
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Amount (€)"))

    class Meta:
        verbose_name = _("Monthly Overhead")
        verbose_name_plural = _("Monthly Overheads")
        indexes = [models.Index(fields=["year", "month", "category"])]

    def __str__(self):
        return f"{self.category.name} - {self.month}/{self.year}: {self.amount} €"


class MjesecniOverheadPregled(models.Model):
    godina = models.PositiveIntegerField(verbose_name=_("Godina"))
    mjesec = models.PositiveIntegerField(verbose_name=_("Mjesec"))
    ukupni_overhead = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Ukupni overhead (€)")
    )

    class Meta:
        verbose_name = _("Mjesečni pregled overhead-a")
        verbose_name_plural = _("Mjesečni pregledi overhead-a")
        indexes = [models.Index(fields=["godina", "mjesec"])]

    def __str__(self):
        return f"Overhead za {self.mjesec}/{self.godina}: {self.ukupni_overhead} €"

    def izracunaj_ukupni_overhead(self):
        from django.db.models import Sum

        ukupno = MonthlyOverhead.objects.filter(year=self.godina, month=self.mjesec).aggregate(
            ukupno=Sum("amount")
        )["ukupno"] or Decimal("0.00")
        self.ukupni_overhead = ukupno
        self.save()
