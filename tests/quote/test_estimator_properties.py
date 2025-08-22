from decimal import Decimal

from hypothesis import assume, given
from hypothesis import strategies as st

from prodaja.services.estimator.dto import ItemInput, QuoteInput
from prodaja.services.estimator.engine import estimate
from prodaja.services.estimator.pricing import money


def make_quote(area, mode="booth", vat_rate=Decimal("0.25")):
    weight = area * 2
    return QuoteInput(
        tenant="t1",
        currency="EUR",
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


@given(st.floats(min_value=0.1, max_value=100))
def test_non_negative(area):
    res = estimate(make_quote(area))["Good"]
    for val in res.components.values():
        assert val >= 0
    assert res.net_total >= 0
    assert res.vat_total >= 0
    assert res.gross_total >= 0


@given(st.floats(min_value=1, max_value=50), st.floats(min_value=1, max_value=50))
def test_monotonic(area1, area2):
    assume(area2 > area1)
    n1 = estimate(make_quote(area1))["Good"].net_total
    n2 = estimate(make_quote(area2))["Good"].net_total
    assert n2 >= n1


@given(st.floats(min_value=1, max_value=40), st.floats(min_value=1, max_value=40))
def test_additivity(a1, a2):
    res1 = estimate(make_quote(a1))["Good"].net_total
    res2 = estimate(make_quote(a2))["Good"].net_total
    combined = estimate(make_quote(a1 + a2))["Good"].net_total
    assert abs((res1 + res2) - combined) <= Decimal("1.00")


@given(st.floats(min_value=1, max_value=100))
def test_dft_increases_paint(area):
    res = estimate(make_quote(area))
    assert res["Better"].components["paint"] >= res["Good"].components["paint"]
    assert res["Best"].components["paint"] >= res["Better"].components["paint"]


@given(st.floats(min_value=1, max_value=100))
def test_conditions_field_more_expensive(area):
    booth = estimate(make_quote(area, mode="booth"))["Good"].components["labor"]
    field = estimate(make_quote(area, mode="field"))["Good"].components["labor"]
    assert field >= booth


@given(st.floats(min_value=1, max_value=100), st.floats(min_value=0.05, max_value=0.30))
def test_vat_consistency(area, vat):
    vat_rate = Decimal(str(vat))
    res = estimate(make_quote(area, vat_rate=vat_rate))["Good"]
    expected_vat = money(res.net_total * vat_rate)
    assert res.vat_total == expected_vat
    assert res.gross_total == res.net_total + res.vat_total


@given(st.floats(min_value=1, max_value=100))
def test_rounding_identity(area):
    res = estimate(make_quote(area))["Good"]
    comp_sum = sum(res.components.values())
    assert comp_sum + res.contingency + res.margin == res.net_total
    assert res.net_total + res.vat_total == res.gross_total
