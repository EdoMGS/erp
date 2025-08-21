"""Paint consumption and cost."""

from __future__ import annotations

from decimal import Decimal

from .dto import ItemInput, PaintSystemSpec
from .pricing import money


def compute_paint(
    item: ItemInput,
    system: PaintSystemSpec,
    price_list: dict,
    norms: dict,
) -> Decimal:
    """Estimate paint cost for an item and paint system."""
    rate = Decimal(str(price_list.get("paint", 0)))
    total_liters = Decimal("0")
    area = Decimal(str(item.area_m2))
    for layer in system.layers:
        dft = Decimal(str(layer.dft_um)) / Decimal("1000")
        solids = Decimal(str(layer.solids_pct)) / Decimal("100")
        if solids == 0:
            continue
        liters = area * dft / solids
        total_liters += liters
    waste_pct = Decimal(str(norms.get("waste_pct", 0)))
    total_liters *= Decimal("1") + waste_pct
    cost = total_liters * rate
    return money(cost)
