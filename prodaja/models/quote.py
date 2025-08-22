from __future__ import annotations

from decimal import Decimal

from django.db import models

from common.models import BaseModel
from tenants.models import Tenant


class Quote(BaseModel):
    STATUS_CHOICES = [
        ("draft", "draft"),
        ("sent", "sent"),
        ("accepted", "accepted"),
        ("expired", "expired"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    number = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="draft")
    valid_until = models.DateField(null=True, blank=True)
    currency = models.CharField(max_length=3)
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2)
    is_vat_registered = models.BooleanField(default=True)
    customer_name = models.CharField(max_length=255)
    customer_vat_id = models.CharField(max_length=64, blank=True, null=True)
    site_address = models.CharField(max_length=255, blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=64, blank=True, null=True)
    lead_source = models.CharField(max_length=64, blank=True, null=True)
    risk_band = models.CharField(max_length=10)
    contingency_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    margin_target_pct = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("0"))
    accepted_at = models.DateTimeField(null=True, blank=True)
    accepted_by = models.CharField(max_length=255, blank=True, null=True)
    acceptance_hash = models.CharField(max_length=128, blank=True, null=True)
    warranty = models.CharField(max_length=255, blank=True, null=True)
    payment_terms = models.CharField(max_length=255, blank=True, null=True)
    revision = models.PositiveIntegerField(default=1)
    attachments = models.JSONField(blank=True, default=list)


class QuoteItem(BaseModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, related_name="items", on_delete=models.CASCADE)
    type = models.CharField(max_length=32)
    description = models.TextField(blank=True)
    uom_base = models.CharField(max_length=16)
    qty_base = models.DecimalField(max_digits=10, decimal_places=2)
    item_ref = models.CharField(max_length=64, blank=True, null=True)
    paint_system_id = models.CharField(max_length=64, blank=True, null=True)


class QuoteOption(BaseModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, related_name="options", on_delete=models.CASCADE)
    name = models.CharField(max_length=32)


class EstimSnapshot(BaseModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, related_name="snapshots", on_delete=models.CASCADE)
    option = models.ForeignKey(
        QuoteOption, related_name="snapshots", on_delete=models.CASCADE, null=True, blank=True
    )
    norms_version = models.CharField(max_length=32)
    price_list_version = models.CharField(max_length=32)
    rounding_policy = models.CharField(max_length=16)
    input_data = models.JSONField()
    breakdown = models.JSONField()
    version = models.CharField(max_length=32)


class QuoteRevision(BaseModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    parent = models.ForeignKey(Quote, related_name="revisions", on_delete=models.CASCADE)
    prev_snapshot = models.ForeignKey(
        EstimSnapshot, related_name="prev_revisions", on_delete=models.SET_NULL, null=True
    )
    new_snapshot = models.ForeignKey(
        EstimSnapshot, related_name="new_revisions", on_delete=models.SET_NULL, null=True
    )
    reason_code = models.CharField(max_length=32)
    delta = models.JSONField(blank=True, default=dict)
