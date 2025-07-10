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
    bank_name = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Naziv banke")
    )
    tip_transakcije = models.CharField(
        max_length=10, choices=TRANSACTION_TYPES, verbose_name=_("Tip transakcije")
    )
    iznos = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Iznos transakcije (€)")
    )
    valuta = models.CharField(max_length=10, default="EUR", verbose_name=_("Valuta"))
    opis = models.CharField(max_length=255, verbose_name=_("Opis transakcije"))
    datum = models.DateField(  # Changed from datum_transakcije
        verbose_name=_("Datum transakcije")
    )
    datum_valute = models.DateField(
        verbose_name=_("Datum valute"), blank=True, null=True
    )
    referenca = models.CharField(
        max_length=100, unique=True, verbose_name=_("Referenca transakcije")
    )
    saldo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Saldo računa (€) nakon transakcije"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Vrijeme evidentiranja u sustavu")
    )

    # Opcionalno, ako želiš označiti da je transakcija usklađena s knjigovodstvom
    is_reconciled = models.BooleanField(
        default=False, verbose_name=_("Usklađeno s knjigovodstvom?")
    )

    def save(self, *args, **kwargs):
        # Ensure proper decimal rounding
        if self.iznos:
            self.iznos = Decimal(str(self.iznos)).quantize(
                Decimal("0.01"), ROUND_HALF_UP
            )
        if self.saldo:
            self.saldo = Decimal(str(self.saldo)).quantize(
                Decimal("0.01"), ROUND_HALF_UP
            )
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
    """
    Primjer dohvaćanja transakcija s bankovnog API-ja i upisa/azuriranja u DB.
    - 'api_url' je endpoint banke
    - 'api_key' je token/ključ za autorizaciju

    U stvarnom životu prilagodi format JSON odgovora
    i mapiranje polja (referenca, datum_valute, ...)
    """
    # Configure retry strategy
    retry_strategy = Retry(
        total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}

    try:
        response = session.get(api_url, headers=headers, timeout=15)
        if response.status_code == 200:
            transakcije = response.json()

            for t in transakcije:
                # Ovisno o JSON formatu prilagodi polja:
                referenca = t.get("reference")  # npr. "TRX12345"
                tip = t.get("type")  # "priljev" ili "odljev"
                iznos = Decimal(str(t.get("amount", "0.00")))
                opis = t.get("description", "")
                datum_trx = t.get("transaction_date")  # "2025-01-01"
                datum_val = t.get("value_date")  # "2025-01-02"
                saldo_str = t.get("balance", "0.00")
                saldo_trx = Decimal(str(saldo_str))
                bank_acc = t.get("iban", "HRxxxxxxxxxxxxx")
                bank_naziv = t.get("bank_name", "Moja Banka")
                currency = t.get("currency", "EUR")

                obj, created = BankTransaction.objects.update_or_create(
                    referenca=referenca,
                    defaults={
                        "tip_transakcije": tip,
                        "iznos": iznos,
                        "opis": opis,
                        "datum": datum_trx,
                        "datum_valute": datum_val,
                        "saldo": saldo_trx,
                        "bank_account_number": bank_acc,
                        "bank_name": bank_naziv,
                        "valuta": currency,
                    },
                )
                if created:
                    logger.info(f"Kreirana nova transakcija s referencom {referenca}")
                else:
                    logger.info(f"Ažurirana transakcija s referencom {referenca}")
        else:
            logger.error(
                f"Greška pri pozivu bankovnog API-ja: Status {response.status_code}"
            )
            raise Exception(
                f"Greška pri povezivanju s bankom, status {response.status_code}"
            )
    except requests.exceptions.RequestException as e:
        logger.error(f"Greška pri komunikaciji s bankom: {e}")
        raise e
    except Exception as e:
        logger.error(f"Fatal error in bank sync: {str(e)}")
        raise


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
