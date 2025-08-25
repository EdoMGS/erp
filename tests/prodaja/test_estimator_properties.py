import json
from decimal import Decimal
from pathlib import Path

from hypothesis import assume, given, settings
from hypothesis import strategies as st

from prodaja.services.estimator.dto import (
    ItemInput,
    LayerSpec,
    PaintSystemSpec,
    QuoteInput,
)
from prodaja.services.estimator.engine import estimate
from prodaja.services.estimator.paint import compute_paint
from prodaja.services.estimator.pricing import money

# Load price list once to derive paint rate
PRICE_LIST_PATH = Path(__file__).resolve().parents[2] / "erp_system/fixtures/price_list.json"
PRICE_LIST = json.loads(PRICE_LIST_PATH.read_text())
PAINT_RATE = Decimal(str(PRICE_LIST["paint"]))


def make_quote(area, mode="booth", vat_rate=Decimal("0.25"), currency="EUR"):
    weight = area * 2
    return QuoteInput(
        tenant="t1",
        currency=currency,
        vat_rate=vat_rate,
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


@settings(max_examples=150, deadline=None)
@given(st.floats(min_value=0.1, max_value=100))
def test_non_negative(area):
    res = estimate(make_quote(area))["Good"]
    for val in res.components.values():
        assert val >= 0
    assert res.net_total >= 0
    assert res.vat_total >= 0
    assert res.gross_total >= 0


@settings(max_examples=150, deadline=None)
@given(
    st.floats(min_value=1, max_value=50),
    st.floats(min_value=1, max_value=50),
)
def test_monotonic(area1, area2):
    assume(area2 > area1)
    n1 = estimate(make_quote(area1))["Good"].net_total
    n2 = estimate(make_quote(area2))["Good"].net_total
    assert n2 >= n1


@settings(max_examples=150, deadline=None)
@given(
    st.floats(min_value=1, max_value=40),
    st.floats(min_value=1, max_value=40),
)
def test_additivity(a1, a2):
    res1 = estimate(make_quote(a1))["Good"].net_total
    res2 = estimate(make_quote(a2))["Good"].net_total
    combined = estimate(make_quote(a1 + a2))["Good"].net_total
    assert abs((res1 + res2) - combined) <= Decimal("1.00")


@settings(max_examples=150, deadline=None)
@given(st.floats(min_value=1, max_value=100))
def test_dft_increases_liters(area):
    res = estimate(make_quote(area))
    liters_good = res["Good"].components["paint"] / PAINT_RATE
    liters_better = res["Better"].components["paint"] / PAINT_RATE
    liters_best = res["Best"].components["paint"] / PAINT_RATE
    assert liters_better >= liters_good
    assert liters_best >= liters_better


@settings(max_examples=150, deadline=None)
@given(
    st.floats(min_value=1, max_value=100),
    st.floats(min_value=0, max_value=0.5),
    st.floats(min_value=0, max_value=0.5),
)
def test_waste_increases_cost(area, waste1, waste2):
    assume(waste2 > waste1)
    item = ItemInput(
        type="fabrication",
        uom_base="m2",
        qty_base=area,
        area_m2=area,
        weight_kg=area * 2,
    )
    system = PaintSystemSpec(
        id="sys", name="sys", layers=[LayerSpec(name="L", dft_um=100, solids_pct=60)]
    )
    norms1 = {"waste_pct": Decimal(str(waste1))}
    norms2 = {"waste_pct": Decimal(str(waste2))}
    cost1 = compute_paint(item, system, PRICE_LIST, norms1)
    cost2 = compute_paint(item, system, PRICE_LIST, norms2)
    assert cost2 >= cost1


@settings(max_examples=150, deadline=None)
@given(st.floats(min_value=1, max_value=100))
def test_conditions_field_more_expensive(area):
    booth = estimate(make_quote(area, mode="booth"))["Good"].components["labor"]
    field = estimate(make_quote(area, mode="field"))["Good"].components["labor"]
    assert field >= booth


@settings(max_examples=150, deadline=None)
@given(
    st.floats(min_value=1, max_value=100),
    st.floats(min_value=0.05, max_value=0.30),
    st.sampled_from(["EUR", "USD", "GBP"]),
)
def test_vat_currency_invariants(area, vat, currency):
    vat_rate = Decimal(str(vat))
    res = estimate(make_quote(area, vat_rate=vat_rate, currency=currency))["Good"]
    expected_vat = money(res.net_total * vat_rate)
    assert res.vat_total == expected_vat
    assert res.gross_total == res.net_total + res.vat_total
    res_eur = estimate(make_quote(area, vat_rate=vat_rate, currency="EUR"))["Good"]
    assert res.net_total == res_eur.net_total


@settings(max_examples=150, deadline=None)
@given(st.floats(min_value=1, max_value=100))
def test_rounding_identity(area):
    res = estimate(make_quote(area))["Good"]
    comp_sum = sum(res.components.values())
    assert comp_sum + res.contingency + res.margin == res.net_total
    assert res.net_total + res.vat_total == res.gross_total
