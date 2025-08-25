from decimal import Decimal

import pytest

from prodaja.services.estimator.dto import ItemInput, QuoteInput
from prodaja.services.estimator.engine import estimate


@pytest.mark.django_db
def test_returns_three_options_positive_values():
    qi = QuoteInput(
        tenant="t1",
        currency="EUR",
        vat_rate=Decimal("0.25"),
        is_vat_registered=True,
        risk_band="Y",
        contingency_pct=Decimal("5"),
        margin_target_pct=Decimal("10"),
        items=[
            ItemInput(
                type="fabrication",
                uom_base="m2",
                qty_base=10.0,
                area_m2=10.0,
                weight_kg=20.0,
                conditions={"mode": "booth"},
            )
        ],
        options=["Good", "Better", "Best"],
    )
    result = estimate(qi)
    assert set(result.keys()) == {"Good", "Better", "Best"}
    for bd in result.values():
        assert bd.net_total > 0
        assert bd.gross_total > 0


@pytest.mark.django_db
def test_monotonic_with_quantity():
    base = QuoteInput(
        tenant="t1",
        currency="EUR",
        vat_rate=Decimal("0.25"),
        is_vat_registered=True,
        risk_band="Y",
        contingency_pct=Decimal("5"),
        margin_target_pct=Decimal("10"),
        items=[ItemInput(type="fab", uom_base="m2", qty_base=10.0, area_m2=10.0, weight_kg=20.0)],
        options=["Good"],
    )
    r1 = estimate(base)["Good"].net_total
    base.items[0].qty_base = 20.0
    base.items[0].area_m2 = 20.0
    base.items[0].weight_kg = 40.0
    r2 = estimate(base)["Good"].net_total
    assert r2 > r1


@pytest.mark.django_db
def test_assumptions_include_versions():
    qi = QuoteInput(
        tenant="t1",
        currency="EUR",
        vat_rate=Decimal("0.25"),
        is_vat_registered=True,
        risk_band="Y",
        contingency_pct=Decimal("5"),
        margin_target_pct=Decimal("10"),
        items=[ItemInput(type="fab", uom_base="m2", qty_base=10.0, area_m2=10.0, weight_kg=20.0)],
        options=["Good"],
    )
    bd = estimate(qi)["Good"]
    a = bd.assumptions
    assert a.get("norms_version")
    assert a.get("price_list_version")
