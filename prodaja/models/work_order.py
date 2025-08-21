from __future__ import annotations

from django.db import models

from common.models import BaseModel
from tenants.models import Tenant

from .quote import Quote


class InventoryLot(BaseModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    sku = models.CharField(max_length=64)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    expiry = models.DateField()


class WorkOrder(BaseModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    quote = models.ForeignKey(Quote, on_delete=models.CASCADE)
    option = models.CharField(max_length=32)

    class Meta:
        unique_together = ("tenant", "quote", "option")


class WorkOrderItem(BaseModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    work_order = models.ForeignKey(WorkOrder, related_name="items", on_delete=models.CASCADE)
    sku = models.CharField(max_length=64)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)


class InventoryReservation(BaseModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    work_order = models.ForeignKey(WorkOrder, related_name="reservations", on_delete=models.CASCADE)
    lot = models.ForeignKey(InventoryLot, on_delete=models.CASCADE)
    sku = models.CharField(max_length=64)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)


class PurchaseRequest(BaseModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    work_order = models.ForeignKey(
        WorkOrder, related_name="purchase_requests", on_delete=models.CASCADE
    )
    sku = models.CharField(max_length=64)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)


class QCPlan(BaseModel):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    work_order = models.ForeignKey(WorkOrder, related_name="qc_plans", on_delete=models.CASCADE)
    corrosion_category = models.CharField(max_length=10)
    dft_points = models.PositiveIntegerField()
    snapshot = models.JSONField(default=dict)
