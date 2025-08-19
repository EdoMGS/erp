from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Dict

from common.money import money

from . import labor, logistics, material, paint, pricing
from .dto import EstimateBreakdown, EstimateComponents, ItemInput, QuoteInput

# Go three levels up: estimator -> services -> prodaja -> repo root
FIXTURES_DIR = Path(__file__).resolve().parents[3] / "erp_system" / "fixtures"


def _load_fixture(name: str) -> Dict:
    with open(FIXTURES_DIR / name, "r", encoding="utf-8") as fh:
        return json.load(fh)


def estimate(quote: QuoteInput) -> EstimateBreakdown:
    """Estimate costs for provided quote input."""
    price_list = _load_fixture("price_list.json")
    norms = _load_fixture("quote_norms.json")

    policy = pricing.RoundingPolicy.PER_ITEM

    option_totals: Dict[str, EstimateComponents] = {}
    for option in quote.options:
        material_total = Decimal("0")
        paint_total = Decimal("0")
        labor_total = Decimal("0")
        logistics_total = Decimal("0")
        for item in quote.items:
            material_total += material.calculate(item, price_list)
            paint_total += paint.calculate(item, option, price_list, norms)
            labor_total += labor.calculate(item, price_list)
            logistics_total += logistics.calculate(item, price_list)
        component_sum = pricing.sum_components(
            [material_total, paint_total, labor_total, logistics_total], policy
        )
        contingency = money(component_sum * quote.contingency_pct)
        margin_base = component_sum + contingency
        margin = money(margin_base * quote.margin_target_pct)
        net_total = money(component_sum + contingency + margin)
        vat_total = money(net_total * quote.vat_rate) if quote.is_vat_registered else Decimal("0")
        gross_total = money(net_total + vat_total)
        option_totals[option] = EstimateComponents(
            material=money(material_total),
            paint=money(paint_total),
            labor=money(labor_total),
            logistics=money(logistics_total),
            contingency=contingency,
            margin=margin,
            net_total=net_total,
            vat_total=vat_total,
            gross_total=gross_total,
        )

    assumptions = {
        "waste_pct": norms.get("default_waste_pct", 0),
        "mode": "booth",
        "height": "<3m",
        "norms_version": norms.get("version"),
        "price_list_version": price_list.get("version"),
        "rounding_policy": policy.value,
        "risk_band": quote.risk_band,
    }
    return EstimateBreakdown(options=option_totals, assumptions=assumptions)
