from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, List, Optional


@dataclass
class LayerSpec:
    name: str
    dft_um: int
    solids_pct: Optional[float] = None
    mix_ratio: Optional[str] = None
    recoat_window: Optional[str] = None
    pot_life: Optional[str] = None


@dataclass
class PaintSystemSpec:
    id: str
    name: str
    brand: str
    layers: List[LayerSpec]


@dataclass
class ItemInput:
    type: str
    weight_kg: float = 0.0
    area_m2: float = 0.0
    length_m: float = 0.0
    uom_base: str = "unit"
    paint_system_id: Optional[str] = None
    conditions: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuoteInput:
    tenant: str
    currency: str
    vat_rate: Decimal
    is_vat_registered: bool
    risk_band: str
    contingency_pct: Decimal
    margin_target_pct: Decimal
    items: List[ItemInput]
    options: List[str]


@dataclass
class EstimateComponents:
    material: Decimal
    paint: Decimal
    labor: Decimal
    logistics: Decimal
    contingency: Decimal
    margin: Decimal
    net_total: Decimal
    vat_total: Decimal
    gross_total: Decimal


@dataclass
class EstimateBreakdown:
    options: Dict[str, EstimateComponents]
    assumptions: Dict[str, Any]
