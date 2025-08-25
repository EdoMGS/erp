from __future__ import annotations

from decimal import Decimal

from django.core.validators import RegexValidator
from django.db import models
from django.utils import timezone

from common.models import BaseModel
from tenants.models import Tenant


class Invoice(BaseModel):
    """Minimal sales invoice model used for posting tests."""

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    number = models.CharField(
        max_length=20,
        validators=[RegexValidator(r"^\d{3}-\d{2}-\d{2}$")],
        help_text="Formatted as NNN-OO-UU",
    )
    issued_at = models.DateTimeField(default=timezone.now)
    operator_mark = models.CharField(max_length=16)
    net_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    vat_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("tenant", "number")

    def __str__(self) -> str:  # pragma: no cover - trivial
        return f"Invoice {self.number}"

    @property
    def net_total(self) -> Decimal:
        return self.net_amount

    def post(self):
        from financije.services.posting_rules import sale_invoice_posted

        return sale_invoice_posted(
            tenant=self.tenant,
            net=self.net_amount,
            vat=self.vat_amount,
            idempotency_key=f"invoice:{self.pk}",
        )
