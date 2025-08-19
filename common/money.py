from decimal import Decimal, ROUND_HALF_UP


def money(value) -> Decimal:
    """Quantize value to two decimal places using ROUND_HALF_UP."""
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
