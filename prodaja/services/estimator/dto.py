"""Dataclasses used by the estimator service."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class LayerSpec:
    name: str
    dft_um: float
    solids_pct: float
    mix_ratio: str | None = None
    recoat_window: float | None = None
    pot_life: float | None = None


@dataclass
class PaintSystemSpec:
    id: str
    name: str
    brand: str | None = None
    layers: list[LayerSpec] = field(default_factory=list)


@dataclass
class ItemInput:
    """Single item that needs to be estimated."""

    type: str
    uom_base: str
    qty_base: float
    area_m2: float = 0.0
    weight_kg: float = 0.0
    paint_system_id: str | None = None
    conditions: dict[str, object] = field(default_factory=dict)


@dataclass
class QuoteInput:
    tenant: str
    currency: str
    vat_rate: Decimal
    is_vat_registered: bool
    risk_band: str
    contingency_pct: Decimal
    margin_target_pct: Decimal
    items: list[ItemInput]
    options: list[str]


@dataclass
class EstimateBreakdown:
    components: dict[str, Decimal]
    contingency: Decimal
    margin: Decimal
    net_total: Decimal
    vat_total: Decimal
    gross_total: Decimal
    assumptions: dict[str, object]
