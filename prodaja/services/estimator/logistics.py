from decimal import Decimal

from .dto import ItemInput
from common.money import money


def calculate(item: ItemInput, price_list: dict) -> Decimal:
    """Calculate logistics cost based on length."""
    rate = Decimal(str(price_list.get("logistics_per_m", 0)))
    length = Decimal(str(item.length_m))
    return money(length * rate)
