from decimal import Decimal

from prodaja.services.estimator.dto import ItemInput, QuoteInput
from prodaja.services.estimator.engine import estimate
from common.money import money


def build_quote(weight, area, length):
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


def test_example_expected_totals():
    quote = build_quote(40, 20, 5)
    result = estimate(quote)
    good = result.options["Good"]
    assert good.net_total == money(Decimal("514.8"))
    assert good.gross_total == money(Decimal("643.5"))


def test_example_scaling():
    quote = build_quote(100, 50, 10)
    result = estimate(quote)
    good = result.options["Good"]
    assert good.net_total == money(Decimal("1280.4"))
    better = result.options["Better"]
    best = result.options["Best"]
    assert good.net_total < better.net_total < best.net_total


def test_logistics_dominates_when_long_distance():
    quote = build_quote(50, 10, 100)
    result = estimate(quote)
    good = result.options["Good"]
    assert good.logistics > good.material
