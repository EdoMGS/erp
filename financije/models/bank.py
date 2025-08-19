# financije/models/bank.py

import logging
from decimal import ROUND_HALF_UP, Decimal

import requests
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class BankTransaction(models.Model):
    """
    Evidencija stvarnih transakcija na bankovnom računu.
    """

    TRANSACTION_TYPES = [
        ("priljev", _("Priljev")),  # npr. "credit" (uplate)
        ("odljev", _("Odljev")),  # npr. "debit" (isplate)
    ]

    # Primjer dodatnih polja:
    bank_account_number = models.CharField(
        max_length=34,
        verbose_name=_("Broj bankovnog računa (IBAN)"),
        help_text=_("IBAN ili broj računa"),
    )
    bank_name = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Naziv banke"))
    tip_transakcije = models.CharField(max_length=10, choices=TRANSACTION_TYPES, verbose_name=_("Tip transakcije"))
    iznos = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Iznos transakcije (€)"))
    valuta = models.CharField(max_length=10, default="EUR", verbose_name=_("Valuta"))
    opis = models.CharField(max_length=255, verbose_name=_("Opis transakcije"))
    datum = models.DateField(verbose_name=_("Datum transakcije"))  # Changed from datum_transakcije
    datum_valute = models.DateField(verbose_name=_("Datum valute"), blank=True, null=True)
    referenca = models.CharField(max_length=100, unique=True, verbose_name=_("Referenca transakcije"))
    saldo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Saldo računa (€) nakon transakcije"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Vrijeme evidentiranja u sustavu"))

    # Opcionalno, ako želiš označiti da je transakcija usklađena s knjigovodstvom
    is_reconciled = models.BooleanField(default=False, verbose_name=_("Usklađeno s knjigovodstvom?"))

    def save(self, *args, **kwargs):
        # Ensure proper decimal rounding
        if self.iznos:
            self.iznos = Decimal(str(self.iznos)).quantize(Decimal("0.01"), ROUND_HALF_UP)
        if self.saldo:
            self.saldo = Decimal(str(self.saldo)).quantize(Decimal("0.01"), ROUND_HALF_UP)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"[{self.tip_transakcije.upper()}] {self.referenca} - {self.iznos} {self.valuta}"

    class Meta:
        verbose_name = _("Bankovna transakcija")
        verbose_name_plural = _("Bankovne transakcije")
        ordering = ["-datum"]  # Updated ordering
        indexes = [
            models.Index(fields=["tip_transakcije"]),
            models.Index(fields=["bank_account_number"]),
        ]


def sinkroniziraj_bankovne_transakcije(api_url, api_key):
    """Thin wrapper kept for backwards compatibility – delegates to services.bank_sync.sync_bank_transactions."""
    from financije.services.bank_sync import sync_bank_transactions

    return sync_bank_transactions(api_url=api_url, api_key=api_key)


class CashFlow(models.Model):
    """
    Jednostavna evidencija priljeva/odljeva za brzi uvid u tok novca
    (po datumu). Obično se radi sumarnije od bankovnih transakcija.
    """

    tip_transakcije = models.CharField(max_length=50)
    iznos = models.DecimalField(max_digits=12, decimal_places=2)
    opis = models.CharField(max_length=255)
    datum = models.DateField()

    # Ako želiš povezati s konkretnom bankovnom transakcijom:
    bank_transaction = models.OneToOneField(
        BankTransaction,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cashflow_entry",
    )

    def __str__(self):
        return f"{self.datum} - {self.iznos} EUR - {self.tip_transakcije}"

    class Meta:
        verbose_name = _("CashFlow")
        verbose_name_plural = _("CashFlows")
        ordering = ["-datum"]


@receiver(post_save, sender=BankTransaction)
def auto_create_cashflow(sender, instance, created, **kwargs):
    """
    Kad se kreira nova BankTransaction, automatski kreiraj CashFlow zapis.
    """
    if created:
        # mapiraj tip i polja
        CashFlow.objects.create(
            tip_transakcije=instance.tip_transakcije,
            iznos=instance.iznos,
            opis=instance.opis,
            datum=instance.datum,
            bank_transaction=instance,
        )
