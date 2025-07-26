from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

try:
    from client_app.models import ClientSupplier
except ImportError:
    ClientSupplier = None


class Invoice(models.Model):
    PAYMENT_METHODS = [
        ("gotovina", "Gotovina"),
        ("kartica", "Kartica"),
        ("virman", "Virman"),
    ]

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("odobreno", "Odobreno"),
        ("otkazano", "Otkazano"),
    ]

    client = models.ForeignKey(
        "client_app.ClientSupplier",  # Use string reference
        on_delete=models.CASCADE,
        related_name="invoices",
        verbose_name=_("Klijent"),
    )
    invoice_number = models.CharField(max_length=100, unique=True, verbose_name=_("Broj fakture"), db_index=True)
    issue_date = models.DateField(verbose_name=_("Datum izdavanja"))
    due_date = models.DateField(verbose_name=_("Datum dospijeća"))
    pdv_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("25.00"),
        verbose_name=_("Stopa PDV-a (%)"),
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        default="virman",
        verbose_name=_("Način plaćanja"),
    )
    status_fakture = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status fakture"),
    )
    paid = models.BooleanField(default=False, verbose_name=_("Plaćeno"))
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_("Kreirao"),
    )
    is_guaranteed = models.BooleanField(default=False, verbose_name=_("Garancija?"))
    guarantee_details = models.TextField(blank=True, null=True, verbose_name=_("Detalji garancije"))
    financial_guarantee = models.BooleanField(default=False, verbose_name=_("Financijska garancija?"))
    tender_statement = models.TextField(blank=True, null=True, verbose_name=_("Izjava za tender"))
    public_tender_ref = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("Referenca javnog natječaja"),
    )

    @property
    def amount(self):
        """Calculate total from line items"""
        return sum(line.line_total for line in self.lines.all())

    @property
    def pdv_amount(self):
        """Calculate total tax from line items"""
        return sum(line.tax_amount for line in self.lines.all())

    def __str__(self):
        return f"Invoice {self.invoice_number}"

    class Meta:
        verbose_name = _("Faktura")
        verbose_name_plural = _("Fakture")
        indexes = [
            models.Index(fields=["issue_date"]),
            models.Index(fields=["due_date"]),
        ]
        ordering = ["-issue_date"]

    def clean(self):
        if self.due_date < self.issue_date:
            raise ValidationError(_("Datum dospijeća ne može biti prije datuma izdavanja"))


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="lines", on_delete=models.CASCADE)
    description = models.CharField(max_length=255, verbose_name=_("Opis stavke"))
    quantity = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Količina"))
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Jedinična cijena"))
    tax_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("25.00"),
        verbose_name=_("Stopa PDV-a"),
    )

    @property
    def line_total(self):
        return self.quantity * self.unit_price

    @property
    def tax_amount(self):
        return self.line_total * (self.tax_rate / Decimal("100.00"))

    class Meta:
        verbose_name = _("Stavka računa")
        verbose_name_plural = _("Stavke računa")


class Payment(models.Model):
    related_invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    # ...existing code...


class Debt(models.Model):
    client = models.ForeignKey(
        "client_app.ClientSupplier",  # Use string reference
        on_delete=models.CASCADE,
        verbose_name=_("Client"),
    )
    invoice = models.ForeignKey(
        Invoice,
        on_delete=models.CASCADE,
        related_name="debts",
        verbose_name=_("Invoice"),
    )
    due_date = models.DateField(verbose_name=_("Due Date"))
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount Due"))
    is_paid = models.BooleanField(default=False, verbose_name=_("Is Paid"))

    def days_overdue(self):
        if not self.is_paid and self.due_date:
            from django.utils import timezone

            today = timezone.now().date()
            return (today - self.due_date).days if today > self.due_date else 0
        return 0

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return f"Debt for Invoice {self.invoice.invoice_number}"
