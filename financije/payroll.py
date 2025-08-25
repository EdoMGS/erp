"""Simplified Croatian payroll calculator.

Provides minimal PayrollItem and PayrollRun dataclasses that compute
mandatory pension contributions, income tax, and employer health
contribution for 2025.  Profit-share payouts are supported as net
amounts added on top of calculated net salary.

Rates are deliberately simplified for demonstration/testing and are
not intended for production use.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from prodaja.utils.money import money

# Basic 2025 contribution/tax rates (simplified)
PENSION_I = Decimal("0.15")
PENSION_II = Decimal("0.05")
HEALTH = Decimal("0.165")  # employer contribution
TAX_RATE = Decimal("0.20")
DEFAULT_ALLOWANCE = Decimal("530.00")

# Mapping of Croatian JOPPD income codes
PAYROLL_CODES = {
    "RAD": "0001",  # regular employment income
    "BONUS": "0002",  # bonus
    "NAKNADA": "0003",  # allowance
}


@dataclass
class PayrollItem:
    """Single employee payroll line."""

    employee: str
    gross: Decimal
    allowance: Decimal = DEFAULT_ALLOWANCE
    profit_share: Decimal = Decimal("0")

    pension_i: Decimal = field(init=False, default=Decimal("0"))
    pension_ii: Decimal = field(init=False, default=Decimal("0"))
    tax: Decimal = field(init=False, default=Decimal("0"))
    net: Decimal = field(init=False, default=Decimal("0"))
    cost: Decimal = field(init=False, default=Decimal("0"))

    def calculate(self) -> None:
        """Populate contribution, tax, net and cost fields."""

        self.pension_i = money(self.gross * PENSION_I)
        self.pension_ii = money(self.gross * PENSION_II)

        taxable = self.gross - self.pension_i - self.pension_ii - self.allowance
        if taxable < 0:
            taxable = Decimal("0")
        self.tax = money(taxable * TAX_RATE)

        net_salary = self.gross - self.pension_i - self.pension_ii - self.tax
        self.net = money(net_salary) + self.profit_share
        self.cost = money(self.gross + self.gross * HEALTH + self.profit_share)


@dataclass
class PayrollRun:
    """Collection of payroll items for a specific period."""

    period: date
    items: list[PayrollItem]

    def calculate(self) -> None:
        for item in self.items:
            item.calculate()

    @property
    def total_cost(self) -> Decimal:
        return money(sum(item.cost for item in self.items))
