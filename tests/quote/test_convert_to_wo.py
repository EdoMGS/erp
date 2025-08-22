import datetime
from decimal import Decimal

import pytest
from rest_framework.test import APIClient

from prodaja.models.quote import EstimSnapshot, Quote, QuoteOption
from prodaja.models.work_order import (
    InventoryLot,
    InventoryReservation,
    PurchaseRequest,
    QCPlan,
    WorkOrder,
)
from tenants.models import Tenant


@pytest.mark.django_db
def test_convert_to_work_order_idempotent_fefo_and_isolated():
    t1 = Tenant.objects.create(name="t1", domain="t1")
    t2 = Tenant.objects.create(name="t2", domain="t2")

    quote = Quote.objects.create(
        tenant=t1,
        number="Q1",
        currency="EUR",
        vat_rate=Decimal("0.25"),
        is_vat_registered=True,
        customer_name="Cust",
        risk_band="Y",
    )
    opt = QuoteOption.objects.create(tenant=t1, quote=quote, name="Good")
    EstimSnapshot.objects.create(
        tenant=t1,
        quote=quote,
        option=opt,
        norms_version="1",
        price_list_version="1",
        rounding_policy="item",
        input_data={"items": [{"area_m2": 50}], "corrosion_category": "C3"},
        breakdown={"bom": [{"paint_system_id": "PS1", "liters": 10}]},
        version="1",
    )

    InventoryLot.objects.create(
        tenant=t1,
        sku="PS1_A",
        quantity=Decimal("2"),
        expiry=datetime.date(2024, 1, 1),
    )
    InventoryLot.objects.create(
        tenant=t1,
        sku="PS1_A",
        quantity=Decimal("5"),
        expiry=datetime.date(2025, 1, 1),
    )
    InventoryLot.objects.create(
        tenant=t2,
        sku="PS1_A",
        quantity=Decimal("5"),
        expiry=datetime.date(2023, 1, 1),
    )
    InventoryLot.objects.create(
        tenant=t1,
        sku="PS1_B",
        quantity=Decimal("1"),
        expiry=datetime.date(2024, 1, 1),
    )

    client = APIClient()
    resp1 = client.post(
        f"/api/quotes/{quote.id}/to-wo",
        {"option": "Good"},
        format="json",
        HTTP_X_TENANT="t1",
    )
    assert resp1.status_code == 200
    wo_id = resp1.data["work_order_id"]
    assert WorkOrder.objects.filter(id=wo_id).exists()

    wo = WorkOrder.objects.get(id=wo_id)
    first_res = (
        InventoryReservation.objects.filter(work_order=wo, sku="PS1_A")
        .order_by("lot__expiry")
        .first()
    )
    assert first_res.lot.expiry == datetime.date(2024, 1, 1)

    prs = list(PurchaseRequest.objects.filter(work_order=wo).values_list("sku", "quantity"))
    assert ("PS1_B", Decimal("2")) in prs
    assert ("PS1_T", Decimal("1")) in prs

    qc = QCPlan.objects.get(work_order=wo)
    assert qc.dft_points > 0

    resp2 = client.post(
        f"/api/quotes/{quote.id}/to-wo",
        {"option": "Good"},
        format="json",
        HTTP_X_TENANT="t1",
    )
    assert resp2.status_code == 200
    assert WorkOrder.objects.filter(tenant=t1).count() == 1
    assert InventoryReservation.objects.filter(work_order=wo).count() == 3
    assert PurchaseRequest.objects.filter(work_order=wo).count() == 2
    assert WorkOrder.objects.filter(tenant=t2).count() == 0
