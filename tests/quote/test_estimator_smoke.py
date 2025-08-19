from decimal import Decimal

from prodaja.services.estimator.dto import ItemInput, QuoteInput
from prodaja.services.estimator.engine import estimate


def _base_quote(weight, area, length):
    item = ItemInput(type="fabrication", weight_kg=weight, area_m2=area, length_m=length)
    return QuoteInput(
        tenant="demo",
        currency="EUR",
        vat_rate=Decimal("0.25"),
        is_vat_registered=True,
        risk_band="A",
        contingency_pct=Decimal("0.10"),
        margin_target_pct=Decimal("0.20"),
        items=[item],
        options=["Good", "Better", "Best"],
    )


def test_estimator_returns_positive_totals():
    result = estimate(_base_quote(100, 50, 10))
    for opt in ["Good", "Better", "Best"]:
        assert result.options[opt].net_total > 0
    assert result.options["Good"].net_total < result.options["Better"].net_total < result.options["Best"].net_total


def test_estimator_monotonic_with_quantity():
    small = estimate(_base_quote(50, 25, 5))
    large = estimate(_base_quote(100, 50, 10))
    assert small.options["Good"].net_total < large.options["Good"].net_total
