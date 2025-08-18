# prodaja/models.py

"""
MVP subset of sales ('prodaja') models.

ForeignKey references to other legacy apps removed; using primitive stand-ins.
Models kept: SalesOpportunity, FieldVisit, Quotation, SalesOrder, SalesContract, Offer.
"""

from decimal import Decimal

from django.db import models
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
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_("Vrijednost"))
    budget_estimate = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True, verbose_name=_("Budžet (procjena)")
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
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Popust (%)"))
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
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("Ukupan iznos (€)"))
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Popust (%)"))
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
    public_tender_number = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Broj javnog natječaja"))
    bank_guarantee_required = models.BooleanField(default=False, verbose_name=_("Bankarska garancija tražena?"))
    total_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name=_("Ukupan iznos (€)"))
    discount = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name=_("Popust (%)"))
    sales_order = models.OneToOneField(
        SalesOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name="sales_contract"
    )
    delivery_schedule = models.TextField(null=True, blank=True, verbose_name=_("Raspored isporuke"))
    client_specific_reqs = models.TextField(null=True, blank=True, verbose_name=_("Posebni zahtjevi klijenta"))
    related_production_order_ref = models.CharField(max_length=64, blank=True, null=True, verbose_name=_("Ref radnog naloga"))
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
