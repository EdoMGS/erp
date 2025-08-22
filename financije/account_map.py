from collections.abc import Callable
from decimal import Decimal


def sale_invoice_posted(_tenant, payload) -> list[dict]:
    net = Decimal(str(payload["net"]))
    vat = Decimal(str(payload.get("vat", "0.00")))
    return [
        {"account": "120", "debit": net + vat, "credit": Decimal("0.00")},
        {"account": "400", "debit": Decimal("0.00"), "credit": net},
        {"account": "470", "debit": Decimal("0.00"), "credit": vat},
    ]


def purchase_invoice_posted(_tenant, payload) -> list[dict]:
    net = Decimal(str(payload["net"]))
    vat = Decimal(str(payload.get("vat", "0.00")))
    return [
        {"account": "500", "debit": net, "credit": Decimal("0.00")},
        {"account": "471", "debit": vat, "credit": Decimal("0.00")},
        {"account": "220", "debit": Decimal("0.00"), "credit": net + vat},
    ]


def advance_receipt(_tenant, payload) -> list[dict]:
    amount = Decimal(str(payload["amount"]))
    return [
        {"account": "110", "debit": amount, "credit": Decimal("0.00")},
        {"account": "270", "debit": Decimal("0.00"), "credit": amount},
    ]


def advance_settlement(_tenant, payload) -> list[dict]:
    amount = Decimal(str(payload["amount"]))
    return [
        {"account": "270", "debit": amount, "credit": Decimal("0.00")},
        {"account": "120", "debit": Decimal("0.00"), "credit": amount},
    ]


def bank_customer_payment(_tenant, payload) -> list[dict]:
    amount = Decimal(str(payload["amount"]))
    return [
        {"account": "110", "debit": amount, "credit": Decimal("0.00")},
        {"account": "120", "debit": Decimal("0.00"), "credit": amount},
    ]


def bank_supplier_payment(_tenant, payload) -> list[dict]:
    amount = Decimal(str(payload["amount"]))
    return [
        {"account": "220", "debit": amount, "credit": Decimal("0.00")},
        {"account": "110", "debit": Decimal("0.00"), "credit": amount},
    ]


ACCOUNT_RULES: dict[str, Callable] = {
    "SALE_INVOICE_POSTED": sale_invoice_posted,
    "PURCHASE_INVOICE_POSTED": purchase_invoice_posted,
    "ADVANCE_RECEIPT": advance_receipt,
    "ADVANCE_SETTLEMENT": advance_settlement,
    "BANK_CUSTOMER_PAYMENT": bank_customer_payment,
    "BANK_SUPPLIER_PAYMENT": bank_supplier_payment,
}
