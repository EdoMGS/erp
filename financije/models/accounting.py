from decimal import Decimal

from django.conf import settings
from django.contrib.postgres.fields import ArrayField  # type: ignore
from django.db.models import JSONField
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.models import Sum
from django.utils.translation import gettext_lazy as _


class Account(models.Model):
    ACCOUNT_TYPE_CHOICES = [
        ("active", _("Aktiva")),
        ("passive", _("Pasiva")),
        ("income", _("Prihod")),
        ("expense", _("Rashod")),
    ]

    number = models.CharField(max_length=20, unique=True, verbose_name=_("Broj konta"))
    name = models.CharField(max_length=255, verbose_name=_("Naziv konta"))
    account_type = models.CharField(max_length=10, choices=ACCOUNT_TYPE_CHOICES, verbose_name=_("Tip konta"))
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

    def __str__(self):
        return f"{self.number} - {self.name}"

    @property
    def balance(self):
        debit = JournalItem.objects.filter(account=self).aggregate(Sum("debit"))["debit__sum"] or Decimal("0.00")
        credit = JournalItem.objects.filter(account=self).aggregate(Sum("credit"))["credit__sum"] or Decimal("0.00")
        return debit - credit if self.account_type in ["active", "expense"] else credit - debit


class JournalEntry(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, null=True, blank=True, related_name='journal_entries')
    date = models.DateField(verbose_name=_("Datum knjiženja"))
    description = models.TextField(verbose_name=_("Opis transakcije"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Korisnik"),
    )
    # Period locking helper flags
    locked = models.BooleanField(default=False, help_text=_('Zaključana temeljnica (period zaključen)'))

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
        if not self.pk:  # Only check on creation
            self.full_clean()
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        if self.pk and not self.is_balanced():
            raise ValidationError(_("Journal entry must be balanced (debits = credits)"))

    class Meta:
        app_label = "financije"
        indexes = [models.Index(fields=["date"]), models.Index(fields=["created_at"])]

    def __str__(self):
        return f"Journal Entry #{self.id} - {self.date}"


class JournalItem(models.Model):
    entry = models.ForeignKey(JournalEntry, on_delete=models.CASCADE, related_name="journalitem_set")
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    debit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    cost_center = models.CharField(max_length=30, null=True, blank=True)
    labels = JSONField(default=list, blank=True, help_text=_('Lista slobodnih oznaka (tagova)'))

    def clean(self):
        if self.debit != Decimal("0.00") and self.credit != Decimal("0.00"):
            raise ValidationError(_("Stavka ne može imati i debit i kredit u isto vrijeme."))

    class Meta:
        app_label = "financije"
        indexes = [
            models.Index(fields=["debit"]),
            models.Index(fields=["credit"]),
        ]

    def __str__(self):
        return f"Journal Item: Entry #{self.entry.id}, Konto {self.account.number}"


class PeriodLock(models.Model):
    tenant = models.ForeignKey('tenants.Tenant', on_delete=models.CASCADE, related_name='period_locks')
    year = models.IntegerField()
    month = models.IntegerField()
    locked_at = models.DateTimeField(auto_now_add=True)
    closed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        app_label = 'financije'
        unique_together = ("tenant", "year", "month")
        indexes = [models.Index(fields=["tenant", "year", "month"])]
        verbose_name = _('Zaključan period')
        verbose_name_plural = _('Zaključani periodi')

    def __str__(self):
        return f"{self.tenant_id or ''} {self.year}-{self.month:02d}"
