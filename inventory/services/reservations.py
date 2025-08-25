from decimal import Decimal

from django.db import transaction

from inventory.models import PaintLot, Reservation


@transaction.atomic
def reserve_paint(*, tenant, work_order, color: str, quantity: Decimal) -> list[Reservation]:
    """Reserve paint lots using FEFO (oldest received first)."""
    remaining = Decimal(quantity)
    lots = (
        PaintLot.objects.select_for_update()
        .filter(tenant=tenant, color=color, remaining_qty__gt=0)
        .order_by("received_at", "id")
    )
    reservations: list[Reservation] = []
    for lot in lots:
        if remaining <= 0:
            break
        take = min(lot.remaining_qty, remaining)
        if take > 0:
            lot.remaining_qty -= take
            lot.save(update_fields=["remaining_qty"])
            reservations.append(
                Reservation.objects.create(
                    tenant=tenant, work_order=work_order, lot=lot, quantity=take
                )
            )
            remaining -= take
    if remaining > 0:
        raise ValueError("Insufficient stock for reservation")
    return reservations
