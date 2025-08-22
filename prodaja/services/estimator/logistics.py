"""Logistics cost estimation."""

from __future__ import annotations

from decimal import Decimal

from .dto import ItemInput
from .pricing import money


def compute_logistics(item: ItemInput, price_list: dict) -> Decimal:
    rate = Decimal(str(price_list.get("logistics", 0)))
    cost = Decimal(str(item.weight_kg)) * Decimal("0.1") * rate
    return money(cost)
