from decimal import Decimal

from django.db import models

from tenants.models import Tenant


class PaintLot(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    color = models.CharField(max_length=32)
    received_at = models.DateField()
    remaining_qty = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))


class Reservation(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    work_order = models.ForeignKey("proizvodnja.RadniNalog", on_delete=models.CASCADE)
    lot = models.ForeignKey(PaintLot, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
