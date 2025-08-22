"""Pricing utilities for the estimator service."""

from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal

ROUNDING_POLICY = "total"


def money(value: float | Decimal) -> Decimal:
    """Return a Decimal rounded to two places using ``ROUND_HALF_UP``."""
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def sum_money(values: dict[str, Decimal]) -> Decimal:
    """Sum a mapping of Decimal values using :func:`money` after each addition."""
    total = Decimal("0")
    for val in values.values():
        total = money(total + val)
    return total
