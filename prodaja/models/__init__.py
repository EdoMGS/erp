"""prodaja.models package

Consolidated sales and invoice models live here (originally in a single models.py file).
The previous intermediary invoice submodule was removed to avoid circular import issues
between admin autodiscovery and a split models package. Django will import this package
as ``prodaja.models`` so all model classes must be defined directly in this namespace.
"""

from decimal import ROUND_HALF_UP, Decimal

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class SalesOpportunity(models.Model):
    STAGE_CHOICES = [
        ("new", _("Novi lead")),
        ("qualified", _("Kvalificiran")),
        ("negotiation", _("Pregovori")),
        ("won", _("Zatvoren - dobiveno")),
        ("lost", _("Zatvoren - izgubljeno")),
    ]
    LEAD_SOURCE_CHOICES = [
        ("field_visit", _("Terenska posjeta")),
        ("tender", _("Javna nabava / natječaj")),
        ("referral", _("Preporuka postojećeg klijenta")),
        ("marketing", _("Digitalni marketing / kampanja")),
        ("trade_fair", _("Sajam / industrijski događaj")),
        ("other", _("Ostalo")),
    ]

    name = models.CharField(max_length=255, verbose_name=_("Naziv prilike"))
    client_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Klijent (naziv)"))
    lead_source = models.CharField(max_length=50, choices=LEAD_SOURCE_CHOICES, default="other")
    stage = models.CharField(max_length=50, choices=STAGE_CHOICES, default="new")
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Vrijednost"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    budget_estimate = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Budžet (procjena)"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    public_tender_number = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Broj javnog natječaja")
    )
    project_service_type = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Vrsta usluge/projekta")
    )
    notes = models.TextField(blank=True, verbose_name=_("Bilješke"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"[{self.stage}] {self.name} - {self.client_name or '-'}"

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("Sales Opportunity")
        verbose_name_plural = _("Sales Opportunities")


class FieldVisit(models.Model):
    STATUS_CHOICES = [
        ("planned", _("Planirano")),
        ("completed", _("Završeno")),
        ("cancelled", _("Otkazano")),
    ]
    opportunity = models.ForeignKey(
        SalesOpportunity,
        on_delete=models.CASCADE,
        related_name="field_visits",
        verbose_name=_("Prodajna prilika"),
    )
    scheduled_date = models.DateField(verbose_name=_("Planirani datum"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="planned", verbose_name=_("Status"))
    notes = models.TextField(blank=True, verbose_name=_("Bilješke"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Field Visit {self.pk} for {self.opportunity.name}"

    class Meta:
        ordering = ["-scheduled_date"]
        verbose_name = _("Field Visit")
        verbose_name_plural = _("Field Visits")


class Quotation(models.Model):
    STATUS_CHOICES = [
        ("draft", _("Nacrt")),
        ("sent", _("Poslano")),
        ("approved", _("Odobreno")),
        ("rejected", _("Odbijeno")),
    ]

    client_name = models.CharField(max_length=255, blank=True, null=True, verbose_name=_("Klijent"))
    opportunity = models.ForeignKey(
        SalesOpportunity, on_delete=models.SET_NULL, null=True, blank=True, related_name="quotations"
    )
    quote_number = models.CharField(max_length=50, unique=True, verbose_name=_("Broj ponude"))
    valid_until = models.DateField(verbose_name=_("Vrijedi do"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("Ukupan iznos (€)"))
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Popust (%)"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    revision_count = models.PositiveIntegerField(default=0, verbose_name=_("Broj revizija"))
    created_by = models.CharField(max_length=255, verbose_name=_("Kreirao/la"))
    linked_production_order_ref = models.CharField(
        max_length=64, blank=True, null=True, verbose_name=_("Ref proizvodnje")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Quotation {self.quote_number}"

    class Meta:
        ordering = ["-created_at"]


class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ("pending", _("Na čekanju")),
        ("completed", _("Završeno")),
        ("cancelled", _("Otkazano")),
    ]

    client_name = models.CharField(max_length=255, verbose_name=_("Klijent"))
    order_number = models.CharField(max_length=50, unique=True, verbose_name=_("Broj narudžbe"))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name=_("Ukupan iznos (€)"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Popust (%)"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    created_by = models.CharField(max_length=255, verbose_name=_("Kreirao/la"))
    quotation = models.ForeignKey(Quotation, on_delete=models.SET_NULL, null=True, blank=True, related_name="orders")
    date_approved_by_client = models.DateField(null=True, blank=True, verbose_name=_("Klijent potvrdio (datum)"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sales Order {self.order_number}"

    class Meta:
        ordering = ["-created_at"]


class SalesContract(models.Model):
    STATUS_CHOICES = [
        ("draft", _("Nacrt")),
        ("active", _("Aktivan")),
        ("closed", _("Zatvoren")),
        ("cancelled", _("Otkazan")),
    ]

    client_name = models.CharField(max_length=255, verbose_name=_("Klijent"))
    contract_number = models.CharField(max_length=50, unique=True, verbose_name=_("Broj ugovora"))
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="draft")
    public_tender_number = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Broj javnog natječaja")
    )
    bank_guarantee_required = models.BooleanField(default=False, verbose_name=_("Bankarska garancija tražena?"))
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        verbose_name=_("Ukupan iznos (€)"),
        validators=[MinValueValidator(Decimal("0"))],
    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Popust (%)"),
        validators=[MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))],
    )
    sales_order = models.OneToOneField(
        SalesOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_contract"
    )
    delivery_schedule = models.TextField(null=True, blank=True, verbose_name=_("Raspored isporuke"))
    client_specific_reqs = models.TextField(null=True, blank=True, verbose_name=_("Posebni zahtjevi klijenta"))
    related_production_order_ref = models.CharField(
        max_length=64, blank=True, null=True, verbose_name=_("Ref radnog naloga")
    )
    created_by = models.CharField(max_length=255, verbose_name=_("Kreirao/la"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sales Contract {self.contract_number}"

    class Meta:
        ordering = ["-created_at"]


class Offer(models.Model):
    customer_name = models.CharField(max_length=255)
    service_lines = models.JSONField(default=list, verbose_name=_("Stavke usluge"))
    material_lines = models.JSONField(default=list, verbose_name=_("Stavke materijala"))
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal("0"), verbose_name=_("Ukupan iznos")
    )
    STATUS_CHOICES = [("draft", _("Nacrt")), ("approved", _("Odobreno"))]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Offer {self.pk}"

    class Meta:
        ordering = ["-created_at"]


from tenants.models import Tenant  # noqa: E402


class Invoice(models.Model):
    STATUS = [
        ("draft", "Draft"),
        ("posted", "Posted"),
        ("cancelled", "Cancelled"),
    ]
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    number = models.CharField(max_length=30, blank=True)
    # Keep default matching migration (timezone.now) to avoid spurious migration
    issue_date = models.DateField(default=timezone.now)
    client_name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS, default="draft")
    currency = models.CharField(max_length=3, default="EUR")
    note = models.TextField(blank=True, default="")
    total_base = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    total_tax = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-issue_date", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "number"],
                name="uniq_invoice_tenant_number_nonblank",
                condition=~Q(number=""),
            )
        ]

    def __str__(self):
        return self.number or f"INV-{self.pk}"

    @property
    def is_posted(self) -> bool:
        return self.status == "posted"

    def recompute_totals(self):
        base = Decimal('0')
        tax = Decimal('0')
        for line in self.lines.all():
            base += line.base_amount
            tax += line.tax_amount
        self.total_base = base
        self.total_tax = tax
        self.total_amount = base + tax

    def assign_number(self):
        if self.number:
            return
        seq = InvoiceSequence.next_number(tenant=self.tenant, year=self.issue_date.year)
        self.number = seq

    def save(self, *args, **kwargs):
        if self.status == "posted" and not self.number:
            self.assign_number()
        super().save(*args, **kwargs)

    def post(self):
        from prodaja.services.invoice_post import post_invoice

        return post_invoice(self)


class InvoiceLine(models.Model):
    invoice = models.ForeignKey(Invoice, related_name="lines", on_delete=models.CASCADE)
    description = models.CharField(max_length=255)
    qty = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('1'))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    tax_rate = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0'))
    base_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    tax_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))
    total_amount = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal('0'))

    def save(self, *args, **kwargs):
        self.base_amount = (self.qty * self.unit_price).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.tax_amount = (self.base_amount * self.tax_rate / Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        self.total_amount = self.base_amount + self.tax_amount
        super().save(*args, **kwargs)
        self.invoice.recompute_totals()
        self.invoice.save(update_fields=["total_base", "total_tax", "total_amount", "updated_at"])


class InvoiceSequence(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    year = models.IntegerField()
    last_number = models.IntegerField(default=0)

    class Meta:
        unique_together = ["tenant", "year"]

    @classmethod
    def next_number(cls, tenant, year: int) -> str:
        from django.db import transaction

        with transaction.atomic():
            obj, _ = cls.objects.select_for_update().get_or_create(tenant=tenant, year=year)
            obj.last_number += 1
            obj.save(update_fields=["last_number"])
        return f"{obj.last_number:03d}-00-00"


from django.db.models.signals import post_delete  # noqa: E402
from django.dispatch import receiver  # noqa: E402


@receiver(post_delete, sender=InvoiceLine)
def _recompute_after_delete(sender, instance, **kwargs):  # pragma: no cover
    inv = instance.invoice
    inv.recompute_totals()
    inv.save(update_fields=["total_base", "total_tax", "total_amount", "updated_at"])


__all__ = [
    "SalesOpportunity",
    "FieldVisit",
    "Quotation",
    "SalesOrder",
    "SalesContract",
    "Offer",
    "Invoice",
    "InvoiceLine",
    "InvoiceSequence",
]
