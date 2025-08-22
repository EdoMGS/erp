from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Sum
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ("active", _("Aktiva")),
        ("passive", _("Pasiva")),
        ("income", _("Prihod")),
        ("expense", _("Rashod")),
    ]

    # --- multi-tenant ---
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="accounts",
        verbose_name=_("Tenant"),
        null=True,
        blank=True,
    )
    number = models.CharField(max_length=20, verbose_name=_("Broj konta"))
    name = models.CharField(max_length=255, verbose_name=_("Naziv konta"))
    account_type = models.CharField(
        max_length=10, choices=ACCOUNT_TYPE_CHOICES, verbose_name=_("Tip konta")
    )
    parent_account = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subaccounts",
        verbose_name=_("Nadređeni konto"),
    )

    class Meta:
        app_label = "financije"
        verbose_name = _("Konto (Account)")
        verbose_name_plural = _("Konta (Accounts)")
        ordering = ["number"]
        constraints = [
            models.UniqueConstraint(fields=["tenant", "number"], name="uniq_account_tenant_number")
        ]

    def __str__(self):
        return f"{self.number} - {self.name}"

    @property
    def balance(self):
        """Return current balance for the account.

        Aktiva (active) and Rashod (expense) konta increase with debit and decrease with
        credit. All others (passive, income) behave inversely.
        """
        debit = JournalItem.objects.filter(account=self).aggregate(Sum("debit"))[
            "debit__sum"
        ] or Decimal("0.00")
        credit = JournalItem.objects.filter(account=self).aggregate(Sum("credit"))[
            "credit__sum"
        ] or Decimal("0.00")
        if self.account_type in {"active", "expense"}:
            return debit - credit
        return credit - debit


class JournalEntry(models.Model):
    # --- multi-tenant & locking/idempotency ---
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="journal_entries",
        verbose_name=_("Tenant"),
        null=True,
        blank=True,
    )
    date = models.DateField(verbose_name=_("Datum knjiženja"))
    description = models.TextField(verbose_name=_("Opis transakcije"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    posted_at = models.DateTimeField(null=True, blank=True)
    locked = models.BooleanField(default=False)
    idempotency_key = models.CharField(max_length=255, unique=True, null=True, blank=True)
    reversal_of = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True, related_name="reversals"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Korisnik"),
    )

    @property
    def total_debit(self):
        return self.journalitem_set.aggregate(total=Sum("debit"))["total"] or Decimal("0.00")

    @property
    def total_credit(self):
        return self.journalitem_set.aggregate(total=Sum("credit"))["total"] or Decimal("0.00")

    def is_balanced(self):
        return self.total_debit == self.total_credit

    @transaction.atomic
    def save(self, *args, **kwargs):
        # Disallow changes once locked
        if self.pk and self.locked:
            raise ValidationError(_("Journal entry is locked and cannot be modified."))
        creating = self.pk is None
        if creating:
            self.full_clean()
        super().save(*args, **kwargs)
        if creating and self.locked and not self.posted_at:
            self.posted_at = timezone.now()
            super().save(update_fields=["posted_at"])

    def clean(self):
        super().clean()
        if self.pk and not self.is_balanced():
            raise ValidationError(_("Journal entry must be balanced (debits = credits)"))

    class Meta:
        app_label = "financije"
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["created_at"]),
            models.Index(fields=["idempotency_key"]),
            models.Index(fields=["tenant", "date"]),
        ]

    def __str__(self):
        return f"Journal Entry #{self.id} - {self.date}"


class JournalItem(models.Model):
    # --- multi-tenant ---
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="journal_items",
        verbose_name=_("Tenant"),
        null=True,
        blank=True,
    )
    entry = models.ForeignKey(
        JournalEntry, on_delete=models.CASCADE, related_name="journalitem_set"
    )
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    def clean(self):
        if self.debit != Decimal("0.00") and self.credit != Decimal("0.00"):
            raise ValidationError(_("Stavka ne može imati i debit i kredit u isto vrijeme."))

    class Meta:
        app_label = "financije"
        indexes = [
            models.Index(fields=["debit"]),
            models.Index(fields=["credit"]),
        ]
        # Enforce: at most one of (debit, credit) is non-zero (allow both zero).
        # i.e. NOT (debit != 0 AND credit != 0)
        constraints = [
            models.CheckConstraint(
                name="journalitem_debit_xor_credit",
                check=~(models.Q(debit__gt=0) & models.Q(credit__gt=0)),
            )
        ]

    def __str__(self):
        return f"Journal Item: Entry #{self.entry.id}, Konto {self.account.number}"

    def save(self, *args, **kwargs):
        # Keep tenant consistent when provided
        if self.entry_id and self.tenant_id and self.entry.tenant_id != self.tenant_id:
            raise ValidationError(_("JournalItem.tenant must equal entry.tenant"))
        if self.account_id and self.tenant_id and self.account.tenant_id != self.tenant_id:
            raise ValidationError(_("JournalItem.tenant must equal account.tenant"))
        super().save(*args, **kwargs)


class PeriodClose(models.Model):
    tenant = models.ForeignKey(
        "tenants.Tenant",
        on_delete=models.CASCADE,
        related_name="period_closes",
        null=True,
        blank=True,
    )
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField(null=True, blank=True)
    closed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tenant", "year", "month")
        indexes = [models.Index(fields=["tenant", "year", "month"])]
        verbose_name = _("Period close")
        verbose_name_plural = _("Period closes")
