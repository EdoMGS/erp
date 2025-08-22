"""Labor cost estimation."""

from __future__ import annotations

from decimal import Decimal

from .dto import ItemInput, PaintSystemSpec
from .pricing import money


def compute_labor(
    item: ItemInput,
    system: PaintSystemSpec,
    price_list: dict,
    norms: dict,
) -> Decimal:
    """Return labor cost for painting based on area and layers."""
    rate = Decimal(str(price_list.get("labor", 0)))
    hours_per_m2 = Decimal(str(norms.get("painting_hours_per_m2_per_layer", 0)))
    layers = Decimal(str(len(system.layers)))
    area = Decimal(str(item.area_m2))
    mode = item.conditions.get("mode", "booth")
    cond_mult = Decimal(str(norms.get("condition_multipliers", {}).get(mode, 1)))
    hours = area * hours_per_m2 * layers * cond_mult
    cost = hours * rate
    return money(cost)
