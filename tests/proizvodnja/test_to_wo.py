from decimal import Decimal
from datetime import date

import pytest

from inventory.models import PaintLot, Reservation
from proizvodnja.services.to_work_order import to_work_order
from tenants.models import Tenant


@pytest.mark.django_db
def test_to_wo_idempotent():
    tenant = Tenant.objects.create(name="T", domain="t")
    lot = PaintLot.objects.create(tenant=tenant, color="red", received_at=date(2024, 1, 1), remaining_qty=Decimal("10"))
    wo1 = to_work_order(tenant=tenant, quote_id=1, option="A", color="red", quantity=Decimal("5"))
    assert PaintLot.objects.get(pk=lot.pk).remaining_qty == Decimal("5")
    wo2 = to_work_order(tenant=tenant, quote_id=1, option="A", color="red", quantity=Decimal("5"))
    assert wo1.pk == wo2.pk
    assert Reservation.objects.filter(work_order=wo1).count() == 1
    assert PaintLot.objects.get(pk=lot.pk).remaining_qty == Decimal("5")


@pytest.mark.django_db
def test_fefo_reservation_uses_oldest_lots_first():
    tenant = Tenant.objects.create(name="T2", domain="t2")
    old_lot = PaintLot.objects.create(tenant=tenant, color="blue", received_at=date(2024, 1, 1), remaining_qty=Decimal("3"))
    new_lot = PaintLot.objects.create(tenant=tenant, color="blue", received_at=date(2024, 2, 1), remaining_qty=Decimal("5"))

    to_work_order(tenant=tenant, quote_id=2, option="A", color="blue", quantity=Decimal("4"))

    old_lot.refresh_from_db()
    new_lot.refresh_from_db()
    assert old_lot.remaining_qty == Decimal("0")
    assert new_lot.remaining_qty == Decimal("4")
