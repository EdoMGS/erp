"""Material cost calculation."""

from __future__ import annotations

from decimal import Decimal

from .dto import ItemInput
from .pricing import money


def compute_material(item: ItemInput, price_list: dict) -> Decimal:
    """Very small heuristic for material costs."""
    rate = Decimal(str(price_list.get("material", 0)))
    cost = rate * Decimal(str(item.weight_kg))
    return money(cost)
