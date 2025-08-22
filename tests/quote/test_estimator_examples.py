from decimal import Decimal

from prodaja.services.estimator.dto import ItemInput, QuoteInput
from prodaja.services.estimator.engine import estimate


def make_quote():
    return QuoteInput(
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
                qty_base=50.0,
                area_m2=50.0,
                weight_kg=100.0,
                conditions={"mode": "booth"},
            )
        ],
        options=["Good", "Better", "Best"],
    )


def test_example_totals_match_expected():
    breakdowns = estimate(make_quote())
    assert breakdowns["Good"].net_total == Decimal("558.25")
    assert breakdowns["Better"].net_total == Decimal("902.83")
    assert breakdowns["Best"].net_total == Decimal("1279.74")
    # ensure order is preserved
    assert (
        breakdowns["Good"].net_total < breakdowns["Better"].net_total < breakdowns["Best"].net_total
    )
