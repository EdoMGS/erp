from __future__ import annotations

from enum import Enum
from decimal import Decimal
from typing import Sequence

from common.money import money


class RoundingPolicy(str, Enum):
    PER_ITEM = "per_item"
    TOTAL = "total"


def sum_components(components: Sequence[Decimal], policy: RoundingPolicy) -> Decimal:
    """Sum components applying rounding policy."""
    if policy == RoundingPolicy.PER_ITEM:
        total = sum(money(c) for c in components)
        return money(total)
    total = sum(components)
    return money(total)
