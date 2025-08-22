"""Estimator engine combining all cost components."""

from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any, cast

from .dto import (
    EstimateBreakdown,
    LayerSpec,
    PaintSystemSpec,
    QuoteInput,
)
from .labor import compute_labor
from .logistics import compute_logistics
from .material import compute_material
from .paint import compute_paint
from .pricing import ROUNDING_POLICY, money, sum_money

BASE_DIR = Path(__file__).resolve().parents[3]


def _load_fixture(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        return cast(dict[str, Any], json.load(fh))


def _load_norms() -> dict:
    return _load_fixture(BASE_DIR / "erp_system/fixtures/quote_norms.json")


def _load_price_list() -> dict:
    return _load_fixture(BASE_DIR / "erp_system/fixtures/price_list.json")


def _parse_paint_systems(norms: dict) -> dict[str, PaintSystemSpec]:
    systems: dict[str, PaintSystemSpec] = {}
    for sys_id, data in norms.get("paint_systems", {}).items():
        layers = [LayerSpec(**layer) for layer in data.get("layers", [])]
        systems[sys_id] = PaintSystemSpec(id=sys_id, name=data.get("name", sys_id), layers=layers)
    return systems


def estimate(quote: QuoteInput) -> dict[str, EstimateBreakdown]:
    """Estimate costs for each option provided in ``quote``."""
    norms = _load_norms()
    price_list = _load_price_list()
    systems = _parse_paint_systems(norms)
    breakdowns: dict[str, EstimateBreakdown] = {}
    for option in quote.options:
        system = systems.get(option)
        material_total = Decimal("0")
        paint_total = Decimal("0")
        labor_total = Decimal("0")
        logistics_total = Decimal("0")
        for item in quote.items:
            material_total += compute_material(item, price_list)
            if system:
                paint_total += compute_paint(item, system, price_list, norms)
                labor_total += compute_labor(item, system, price_list, norms)
            logistics_total += compute_logistics(item, price_list)
        components = {
            "material": money(material_total),
            "paint": money(paint_total),
            "labor": money(labor_total),
            "logistics": money(logistics_total),
        }
        component_sum = sum_money(components)
        contingency = money(component_sum * quote.contingency_pct / Decimal("100"))
        subtotal = money(component_sum + contingency)
        margin = money(subtotal * quote.margin_target_pct / Decimal("100"))
        net_total = money(component_sum + contingency + margin)
        vat_total = money(net_total * quote.vat_rate)
        gross_total = money(net_total + vat_total)
        assumptions = {
            "waste_pct": norms.get("waste_pct"),
            "mode": quote.items[0].conditions.get("mode", "booth") if quote.items else None,
            "norms_version": norms.get("version"),
            "price_list_version": price_list.get("version"),
            "rounding_policy": ROUNDING_POLICY,
            "risk_band": quote.risk_band,
        }
        breakdowns[option] = EstimateBreakdown(
            components=components,
            contingency=contingency,
            margin=margin,
            net_total=net_total,
            vat_total=vat_total,
            gross_total=gross_total,
            assumptions=assumptions,
        )
    return breakdowns
