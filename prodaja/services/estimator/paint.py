from decimal import Decimal

from .dto import ItemInput
from common.money import money


def calculate(item: ItemInput, option: str, price_list: dict, norms: dict) -> Decimal:
    """Calculate paint cost based on area and number of layers for an option."""
    rate = Decimal(str(price_list.get("paint_per_m2_per_layer", 0)))
    layers = norms.get("paint_systems", {}).get(option, {}).get("layers", [])
    layer_count = len(layers) or 1
    area = Decimal(str(item.area_m2))
    return money(area * rate * layer_count)
