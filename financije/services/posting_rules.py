"""Helper functions for explicit ledger postings.

These helpers replace the old signal based implementation by explicitly
calling :func:`financije.ledger.post_transaction` with predefined event
names.
"""

from decimal import Decimal

from financije.ledger import post_transaction


def sale_invoice_posted(
    *,
    tenant,
    net: Decimal,
    vat: Decimal = Decimal("0.00"),
    idempotency_key: str | None = None,
):
    payload = {"net": net, "vat": vat, "description": "sale invoice"}
    return post_transaction(
        tenant=tenant,
        event="SALE_INVOICE_POSTED",
        payload=payload,
        idempotency_key=idempotency_key,
    )


def purchase_invoice_posted(
    *,
    tenant,
    net: Decimal,
    vat: Decimal = Decimal("0.00"),
    idempotency_key: str | None = None,
):
    payload = {"net": net, "vat": vat, "description": "purchase invoice"}
    return post_transaction(
        tenant=tenant,
        event="PURCHASE_INVOICE_POSTED",
        payload=payload,
        idempotency_key=idempotency_key,
    )


def advance_receipt(*, tenant, amount: Decimal, idempotency_key: str | None = None):
    payload = {"amount": amount}
    return post_transaction(
        tenant=tenant,
        event="ADVANCE_RECEIPT",
        payload=payload,
        idempotency_key=idempotency_key,
    )


def advance_settlement(*, tenant, amount: Decimal, idempotency_key: str | None = None):
    payload = {"amount": amount}
    return post_transaction(
        tenant=tenant,
        event="ADVANCE_SETTLEMENT",
        payload=payload,
        idempotency_key=idempotency_key,
    )


def bank_customer_payment(*, tenant, amount: Decimal, idempotency_key: str | None = None):
    payload = {"amount": amount}
    return post_transaction(
        tenant=tenant,
        event="BANK_CUSTOMER_PAYMENT",
        payload=payload,
        idempotency_key=idempotency_key,
    )


def bank_supplier_payment(*, tenant, amount: Decimal, idempotency_key: str | None = None):
    payload = {"amount": amount}
    return post_transaction(
        tenant=tenant,
        event="BANK_SUPPLIER_PAYMENT",
        payload=payload,
        idempotency_key=idempotency_key,
    )


def profit_share_distribution(
    *,
    tenant,
    base: Decimal,
    company: Decimal,
    workers: Decimal,
    owner: Decimal,
    rounding_diff: Decimal = Decimal("0.00"),
    idempotency_key: str | None = None,
):
    payload = {
        "base": base,
        "company": company,
        "workers": workers,
        "owner": owner,
        "rounding_diff": rounding_diff,
        "description": "profit share",
    }
    return post_transaction(
        tenant=tenant,
        event="PROFIT_SHARE",
        payload=payload,
        idempotency_key=idempotency_key,
    )


__all__ = [
    "sale_invoice_posted",
    "purchase_invoice_posted",
    "advance_receipt",
    "advance_settlement",
    "bank_customer_payment",
    "bank_supplier_payment",
    "profit_share_distribution",
]
