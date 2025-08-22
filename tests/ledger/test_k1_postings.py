from decimal import Decimal

import pytest

from financije.ledger import post_transaction
from financije.models import Account, JournalEntry, JournalItem
from tenants.models import Tenant


@pytest.mark.django_db
def test_sale_invoice_posted_balanced_and_idempotent():
    tenant = Tenant.objects.create(name="T1")
    # Minimal COA for test
    ar = Account.objects.create(tenant=tenant, number="120", name="AR", account_type="active")
    rev = Account.objects.create(tenant=tenant, number="400", name="Revenue", account_type="income")
    vatp = Account.objects.create(
        tenant=tenant, number="470", name="VAT payable", account_type="passive"
    )

    net = Decimal("100.00")
    vat = Decimal("25.00")
    idem = f"{tenant.pk}:invoice:1:posted"

    je1 = post_transaction(
        tenant=tenant,
        event="SALE_INVOICE_POSTED",
        payload={"net": net, "vat": vat, "description": "sale"},
        idempotency_key=idem,
    )
    assert isinstance(je1, JournalEntry)
    assert JournalItem.objects.filter(entry=je1).count() == 3
    # Balanced check
    assert je1.total_debit == je1.total_credit == Decimal("125.00")

    # Idempotent
    je2 = post_transaction(
        tenant=tenant,
        event="SALE_INVOICE_POSTED",
        payload={"net": net, "vat": vat, "description": "sale"},
        idempotency_key=idem,
    )
    assert je1.pk == je2.pk

    # Balances
    assert ar.balance == Decimal("125.00")
    assert rev.balance == Decimal("125.00") - Decimal("25.00")  # revenue credit 100 => credit-debit
    assert vatp.balance == Decimal("25.00")  # passive: credit - debit


@pytest.mark.django_db
def test_advance_receipt_and_settlement():
    tenant = Tenant.objects.create(name="T2")
    bank = Account.objects.create(tenant=tenant, number="110", name="Bank", account_type="active")
    adv = Account.objects.create(
        tenant=tenant, number="270", name="Advances", account_type="passive"
    )
    ar = Account.objects.create(tenant=tenant, number="120", name="AR", account_type="active")

    amount = Decimal("300.00")
    post_transaction(tenant=tenant, event="ADVANCE_RECEIPT", payload={"amount": amount})
    assert bank.balance == Decimal("300.00")
    assert adv.balance == Decimal("300.00")

    post_transaction(tenant=tenant, event="ADVANCE_SETTLEMENT", payload={"amount": amount})
    # Advance cleared, AR credited
    assert adv.balance == Decimal("0.00")
    assert ar.balance == Decimal("-300.00")  # active: debit - credit => credited 300 => -300


@pytest.mark.django_db
def test_purchase_invoice_posted():
    tenant = Tenant.objects.create(name="T3")
    exp = Account.objects.create(
        tenant=tenant, number="500", name="Expense", account_type="expense"
    )
    vatr = Account.objects.create(
        tenant=tenant, number="471", name="VAT receivable", account_type="active"
    )
    ap = Account.objects.create(tenant=tenant, number="220", name="AP", account_type="passive")

    net = Decimal("200.00")
    vat = Decimal("50.00")
    post_transaction(
        tenant=tenant, event="PURCHASE_INVOICE_POSTED", payload={"net": net, "vat": vat}
    )

    # Expense (active/expense) debit increases; AP (passive) credit increases; VAT receivable (active) debit increases
    assert exp.balance == Decimal("200.00")
    assert vatr.balance == Decimal("50.00")
    assert ap.balance == Decimal("50.00") + Decimal("200.00")


@pytest.mark.django_db
def test_bank_payments():
    tenant = Tenant.objects.create(name="T4")
    bank = Account.objects.create(tenant=tenant, number="110", name="Bank", account_type="active")
    ar = Account.objects.create(tenant=tenant, number="120", name="AR", account_type="active")
    ap = Account.objects.create(tenant=tenant, number="220", name="AP", account_type="passive")

    # Seed some starting balances by posting entries directly
    post_transaction(
        tenant=tenant, event="BANK_CUSTOMER_PAYMENT", payload={"amount": Decimal("150.00")}
    )
    assert bank.balance == Decimal("150.00")
    assert ar.balance == Decimal("-150.00")

    post_transaction(
        tenant=tenant, event="BANK_SUPPLIER_PAYMENT", payload={"amount": Decimal("40.00")}
    )
    assert bank.balance == Decimal("110.00")  # 150 - 40
    assert ap.balance == Decimal("-40.00")  # passive: credit - debit; debited 40 => -40
