# financije/models/others.py

from decimal import Decimal

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _

# client_app (za ClientSupplier)
try:
    from client_app.models import ClientSupplier
except ImportError:
    ClientSupplier = None

class NekiFinancijskiModel(models.Model):
    """
    Samo placeholder za razne financijske modele
    koje ne želiš izdvajati u poseban fajl.
    """
    pass


class FinancialDetails(models.Model):
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Ukupna cijena")
    )
    vat_rate = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        default=Decimal('25.00'),
        verbose_name=_("Stopa PDV-a")
    )
    contracted_net_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        default=Decimal('0.00'),
        verbose_name=_("Ugovorena neto cijena")
    )
    contracted_gross_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        default=Decimal('0.00'),
        verbose_name=_("Ugovorena bruto cijena")
    )
    predicted_costs = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        default=Decimal('0.00'),
        verbose_name=_("Predviđeni troškovi")
    )
    actual_costs = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Stvarni troškovi")
    )
    predicted_profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        blank=True,
        null=True,
        default=Decimal('0.00'),
        verbose_name=_("Predviđena dobit")
    )
    actual_profit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Stvarna dobit (€)")
    )

    def __str__(self):
        return f"Financijski detalji ID {self.id}"

    class Meta:
        verbose_name = _("Financial Details")
        verbose_name_plural = _("Financial Details")


class VariablePayRule(models.Model):
    position = models.ForeignKey(
        'ljudski_resursi.Position',
        on_delete=models.CASCADE,
        verbose_name=_("Pozicija")
    )
    expertise_level = models.ForeignKey(
        'ljudski_resursi.ExpertiseLevel',
        on_delete=models.CASCADE,
        default=1,
        verbose_name=_("Razina stručnosti")
    )
    variable_pay = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Varijabilni dio (€)")
    )
    bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Bonus (€)")
    )

    class Meta:
        unique_together = ('position', 'expertise_level')
        verbose_name = _("Pravilo za varijabilni dio plaće")
        verbose_name_plural = _("Pravila za varijabilni dio plaće")

    def __str__(self):
        return f"{self.position} - {self.expertise_level}"


class SalesContract(models.Model):
    contract_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_("Contract Number")
    )
    client = models.ForeignKey(
        ClientSupplier,
        on_delete=models.CASCADE,
        verbose_name=_("Client")
    )

    def __str__(self):
        return f"Sales Contract {self.contract_number} for {self.client}"


class FinancijskaTransakcija(models.Model):
    """
    Primjer generičke financijske transakcije
    povezive s bilo kojim objektom (generički fk).
    """
    datum = models.DateTimeField(auto_now_add=True)
    iznos = models.DecimalField(max_digits=10, decimal_places=2)
    opis = models.TextField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Racun(models.Model):
    """
    Račun - može biti izlazni ili ulazni, 
    povezan s drugim aplikacijama (nabava, skladiste, projektiranje...).
    """
    broj = models.CharField(max_length=20)
    datum = models.DateField()
    iznos = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', _('Nacrt')),
            ('issued', _('Izdan')),
            ('paid', _('Plaćen')),
            ('canceled', _('Storniran')),
        ],
        default='draft'
    )

    primka = models.OneToOneField(
        'skladiste.Primka',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='racun'
    )

    class Meta:
        verbose_name = _("Račun")
        verbose_name_plural = _("Računi")
        ordering = ['-datum']
        indexes = [
            models.Index(fields=['broj']),
            models.Index(fields=['datum']),
        ]

    def __str__(self):
        return f"Račun {self.broj}"


class FinancialAnalysis(models.Model):
    """Financial analysis model for tenders and other business processes"""
    total_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Total Cost")
    )
    expected_profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Expected Profit")
    )
    risk_assessment = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Risk Assessment")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Financial Analysis")
        verbose_name_plural = _("Financial Analyses")

    def __str__(self):
        return f"Financial Analysis #{self.pk}"


