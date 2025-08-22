from decimal import Decimal

from financije.ledger import post_transaction


def post_customer_payment(tenant, amount: Decimal, date, description: str = ""):
    payload = {"date": date, "amount": amount, "description": description}
    post_transaction(
        tenant=tenant,
        event="BANK_CUSTOMER_PAYMENT",
        payload=payload,
        idempotency_key=f"{getattr(tenant, 'id', 'na')}:bank:customer:{date}:{amount}",
        lock=True,
    )


def post_supplier_payment(tenant, amount: Decimal, date, description: str = ""):
    payload = {"date": date, "amount": amount, "description": description}
    post_transaction(
        tenant=tenant,
        event="BANK_SUPPLIER_PAYMENT",
        payload=payload,
        idempotency_key=f"{getattr(tenant, 'id', 'na')}:bank:supplier:{date}:{amount}",
        lock=True,
    )
