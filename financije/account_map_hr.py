"""Mapping of Croatian accounting events to posting functions."""

from collections.abc import Callable
from decimal import Decimal


def sale_invoice_posted(_tenant, payload: dict) -> list[dict]:
    """Post a domestic sales invoice with VAT."""
    net = Decimal(str(payload["net"]))
    vat = Decimal(str(payload.get("vat", "0.00")))
    return [
        {"account": "1200", "debit": net + vat, "credit": Decimal("0.00")},
        {"account": "7600", "debit": Decimal("0.00"), "credit": net},
        {"account": "4700", "debit": Decimal("0.00"), "credit": vat},
    ]


def advance_receipt(_tenant, payload: dict) -> list[dict]:
    """Customer pays an advance which creates a liability."""
    amount = Decimal(str(payload["amount"]))
    return [
        {"account": "1000", "debit": amount, "credit": Decimal("0.00")},
        {"account": "2200", "debit": Decimal("0.00"), "credit": amount},
    ]


def advance_settlement(_tenant, payload: dict) -> list[dict]:
    """Settle an advance against an issued invoice."""
    amount = Decimal(str(payload["amount"]))
    return [
        {"account": "2200", "debit": amount, "credit": Decimal("0.00")},
        {"account": "1200", "debit": Decimal("0.00"), "credit": amount},
    ]


def purchase_invoice_posted(_tenant, payload: dict) -> list[dict]:
    """Post an incoming supplier invoice with deductible VAT."""
    net = Decimal(str(payload["net"]))
    vat = Decimal(str(payload.get("vat", "0.00")))
    return [
        {"account": "4000", "debit": net, "credit": Decimal("0.00")},
        {"account": "1400", "debit": vat, "credit": Decimal("0.00")},
        {"account": "2200", "debit": Decimal("0.00"), "credit": net + vat},
    ]


def bank_customer_payment(_tenant, payload: dict) -> list[dict]:
    """Customer pays an invoice via bank transfer."""
    amount = Decimal(str(payload["amount"]))
    return [
        {"account": "1000", "debit": amount, "credit": Decimal("0.00")},
        {"account": "1200", "debit": Decimal("0.00"), "credit": amount},
    ]


def bank_supplier_payment(_tenant, payload: dict) -> list[dict]:
    """Pay a supplier invoice from the bank account."""
    amount = Decimal(str(payload["amount"]))
    return [
        {"account": "2200", "debit": amount, "credit": Decimal("0.00")},
        {"account": "1000", "debit": Decimal("0.00"), "credit": amount},
    ]


def rc_construction(_tenant, payload: dict) -> list[dict]:
    """Reverse charge for construction services."""
    net = Decimal(str(payload["net"]))
    vat = Decimal(str(payload.get("vat", "0.00")))
    return [
        {"account": "4000", "debit": net, "credit": Decimal("0.00")},
        {"account": "2200", "debit": Decimal("0.00"), "credit": net},
        {"account": "1400", "debit": vat, "credit": Decimal("0.00")},
        {"account": "4700", "debit": Decimal("0.00"), "credit": vat},
    ]


def ic_acquisition(_tenant, payload: dict) -> list[dict]:
    """Intracommunity acquisition with self-assessed VAT."""
    net = Decimal(str(payload["net"]))
    vat = Decimal(str(payload.get("vat", "0.00")))
    return [
        {"account": "3000", "debit": net, "credit": Decimal("0.00")},
        {"account": "2200", "debit": Decimal("0.00"), "credit": net},
        {"account": "1400", "debit": vat, "credit": Decimal("0.00")},
        {"account": "4700", "debit": Decimal("0.00"), "credit": vat},
    ]


def sale_export(_tenant, payload: dict) -> list[dict]:
    """Export sale at 0% VAT."""
    net = Decimal(str(payload["net"]))
    return [
        {"account": "1200", "debit": net, "credit": Decimal("0.00")},
        {"account": "7600", "debit": Decimal("0.00"), "credit": net},
    ]


def profit_share(_tenant, payload: dict) -> list[dict]:
    """Distribute annual profit between company, workers and owner."""
    base = Decimal(str(payload["base"]))
    company = Decimal(str(payload["company"]))
    workers = Decimal(str(payload["workers"]))
    owner = Decimal(str(payload["owner"]))
    diff = Decimal(str(payload.get("rounding_diff", "0")))
    lines = [
        {"account": "6300", "debit": base, "credit": Decimal("0.00")},
        {"account": "2600", "debit": Decimal("0.00"), "credit": company},
        {"account": "2601", "debit": Decimal("0.00"), "credit": workers},
        {"account": "8400", "debit": Decimal("0.00"), "credit": owner},
    ]
    if diff != Decimal("0"):
        if diff > 0:
            lines.append({"account": "4999", "debit": Decimal("0.00"), "credit": diff})
        else:
            lines.append({"account": "4999", "debit": -diff, "credit": Decimal("0.00")})
    return lines


ACCOUNT_RULES: dict[str, Callable] = {
    "SALE_INVOICE_POSTED": sale_invoice_posted,
    "ADVANCE_RECEIPT": advance_receipt,
    "ADVANCE_SETTLEMENT": advance_settlement,
    "PURCHASE_INVOICE_POSTED": purchase_invoice_posted,
    "BANK_CUSTOMER_PAYMENT": bank_customer_payment,
    "BANK_SUPPLIER_PAYMENT": bank_supplier_payment,
    "RC_CONSTRUCTION": rc_construction,
    "IC_ACQUISITION": ic_acquisition,
    "SALE_EXPORT": sale_export,
    "PROFIT_SHARE": profit_share,
}
