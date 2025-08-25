"""Minimal VAT engine and books for Croatian PDV reporting.

This module defines simple data structures to represent VAT codes and
book entries for sales (IRA) and purchases (URA).  It also provides an
``aggregate_pdv_o`` helper that sums the books into a structure that can
be later serialized to the official PDV-O form.

Only a subset of PDV scenarios is supported: standard 25% rate, reduced
13% rate, reverse charge (RC), intra-community acquisition (IC-acq) and
0% export.  The goal is to provide a thin, well tested abstraction that
can be expanded with real regulatory mappings.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum


class VatType(str, Enum):
    """Enumeration of supported VAT scenarios."""

    STANDARD = "25"  # domestic 25% supplies
    REDUCED_13 = "13"  # domestic 13% supplies
    REVERSE_CHARGE = "rc"  # reverse-charge domestic services
    IC_ACQ = "ic_acq"  # intra-community acquisition
    EXPORT = "export"  # 0% export


@dataclass(frozen=True)
class VatCode:
    """Descriptor for a VAT rate and its regulatory type."""

    rate: Decimal
    type: VatType


@dataclass(frozen=True)
class VatBookEntry:
    """A single entry in the VAT book (IRA/URA)."""

    kind: str  # "sale" or "purchase"
    vat_code: VatCode
    base: Decimal

    @property
    def vat(self) -> Decimal:
        return (self.base * self.vat_code.rate).quantize(Decimal("0.01"))


def _blank_totals() -> dict[str, dict[str, Decimal]]:
    zero = Decimal("0.00")
    return {vt.value: {"base": zero, "vat": zero} for vt in VatType}


def aggregate_pdv_o(
    sales: Iterable[VatBookEntry],
    purchases: Iterable[VatBookEntry],
) -> dict[str, dict[str, dict[str, Decimal]]]:
    """Aggregate sale and purchase VAT books into PDV-O totals.

    RC and IC-acq purchases contribute to both output and input tax,
    therefore they are included in the sales and purchases side.
    """

    totals = {"sales": _blank_totals(), "purchases": _blank_totals()}

    def add(kind: str, vat_type: VatType, base: Decimal, vat: Decimal) -> None:
        bucket = totals[kind][vat_type.value]
        bucket["base"] += base
        bucket["vat"] += vat

    for entry in sales:
        add("sales", entry.vat_code.type, entry.base, entry.vat)

    for entry in purchases:
        add("purchases", entry.vat_code.type, entry.base, entry.vat)
        if entry.vat_code.type in {VatType.REVERSE_CHARGE, VatType.IC_ACQ}:
            # self-accounting: same amounts on the sales side
            add("sales", entry.vat_code.type, entry.base, entry.vat)

    # round all totals to cents
    for side in totals.values():
        for bucket in side.values():
            bucket["base"] = bucket["base"].quantize(Decimal("0.01"))
            bucket["vat"] = bucket["vat"].quantize(Decimal("0.01"))

    return totals
