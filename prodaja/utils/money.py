"""Money helper used across prodaja.

Thin wrapper around estimator.pricing.money so other modules can import a single place.
"""

from __future__ import annotations

from decimal import Decimal

from prodaja.services.estimator.pricing import money as _money


def money(amount: Decimal | float) -> Decimal:
    return _money(amount)
