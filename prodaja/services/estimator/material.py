from decimal import Decimal

from .dto import ItemInput
from common.money import money


def calculate(item: ItemInput, price_list: dict) -> Decimal:
    """Calculate material cost for an item."""
    rate = Decimal(str(price_list.get("material_per_kg", 0)))
    return money(Decimal(str(item.weight_kg)) * rate)
