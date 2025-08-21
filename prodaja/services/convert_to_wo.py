from __future__ import annotations

from decimal import Decimal
from math import ceil

from django.db import transaction

from tenants.models import Tenant

from ..models.quote import EstimSnapshot, Quote, QuoteOption
from ..models.work_order import (
    InventoryLot,
    InventoryReservation,
    PurchaseRequest,
    QCPlan,
    WorkOrder,
    WorkOrderItem,
)


def _split_paint(paint_id: str, liters: Decimal) -> list[tuple[str, Decimal]]:
    return [
        (f"{paint_id}_A", liters * Decimal("0.6")),
        (f"{paint_id}_B", liters * Decimal("0.3")),
        (f"{paint_id}_T", liters * Decimal("0.1")),
    ]


def convert_to_work_order(tenant: Tenant, quote_id: int, option_name: str) -> WorkOrder:
    quote = Quote.objects.get(id=quote_id, tenant=tenant)
    option = QuoteOption.objects.get(quote=quote, tenant=tenant, name=option_name)
    work_order, created = WorkOrder.objects.get_or_create(
        tenant=tenant, quote=quote, option=option_name
    )
    if not created:
        return work_order

    snapshot = (
        EstimSnapshot.objects.filter(tenant=tenant, quote=quote, option=option)
        .order_by("-created_at")
        .first()
    )
    if not snapshot:
        raise ValueError("No snapshot for option")

    bom_entries: list[tuple[str, Decimal]] = []
    for entry in snapshot.breakdown.get("bom", []):
        if "sku" in entry:
            bom_entries.append((entry["sku"], Decimal(str(entry["qty"]))))
        elif "paint_system_id" in entry:
            liters = Decimal(str(entry.get("liters", 0)))
            bom_entries.extend(_split_paint(entry["paint_system_id"], liters))

    with transaction.atomic():
        for sku, qty in bom_entries:
            WorkOrderItem.objects.create(
                tenant=tenant, work_order=work_order, sku=sku, quantity=qty
            )
            remaining = qty
            lots = InventoryLot.objects.filter(tenant=tenant, sku=sku).order_by("expiry")
            for lot in lots:
                if remaining <= 0:
                    break
                take = min(remaining, lot.quantity)
                if take > 0:
                    InventoryReservation.objects.create(
                        tenant=tenant,
                        work_order=work_order,
                        lot=lot,
                        sku=sku,
                        quantity=take,
                    )
                    remaining -= take
            if remaining > 0:
                PurchaseRequest.objects.create(
                    tenant=tenant, work_order=work_order, sku=sku, quantity=remaining
                )

        items = snapshot.input_data.get("items", [])
        area = sum(Decimal(str(i.get("area_m2", 0))) for i in items)
        category = snapshot.input_data.get("corrosion_category", "C3")
        divisor_map = {
            "C2": Decimal("30"),
            "C3": Decimal("25"),
            "C4": Decimal("20"),
            "C5": Decimal("15"),
            "C5-M": Decimal("10"),
        }
        divisor = divisor_map.get(category, Decimal("25"))
        points = int(ceil((area / divisor) if divisor else Decimal("0")))
        QCPlan.objects.create(
            tenant=tenant,
            work_order=work_order,
            corrosion_category=category,
            dft_points=points,
            snapshot={"area_m2": float(area)},
        )
    return work_order
