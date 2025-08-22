from decimal import Decimal

from prodaja.services.estimator.dto import ItemInput, QuoteInput
from prodaja.services.estimator.engine import estimate


def make_quote(area=50.0, weight=100.0, mode="booth"):
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
                qty_base=area,
                area_m2=area,
                weight_kg=weight,
                conditions={"mode": mode},
            )
        ],
        options=["Good", "Better", "Best"],
    )


def test_smoke_three_options_positive_totals():
    quote = make_quote()
    breakdowns = estimate(quote)
    assert set(breakdowns.keys()) == {"Good", "Better", "Best"}
    for bd in breakdowns.values():
        assert bd.net_total > 0
        assert bd.vat_total > 0
        assert bd.gross_total > 0


def test_monotonic_increase_with_area():
    small = estimate(make_quote(area=10.0))["Good"].net_total
    large = estimate(make_quote(area=20.0))["Good"].net_total
    assert large > small
