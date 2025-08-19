from decimal import Decimal

from .dto import ItemInput
from common.money import money


def calculate(item: ItemInput, price_list: dict) -> Decimal:
    """Calculate labor cost based on area."""
    rate = Decimal(str(price_list.get("labor_per_m2", 0)))
    area = Decimal(str(item.area_m2))
    return money(area * rate)
