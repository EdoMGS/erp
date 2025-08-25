from datetime import date
from decimal import Decimal

import pytest

from financije.ledger import post_transaction
from financije.models import Account
from financije.reports import (
    ar_ap_aging,
    balance_sheet_light,
    pnl_light,
    related_party_ledger,
)
from tenants.models import Tenant


@pytest.mark.django_db
def test_reports_compute_expected_values():
    tenant = Tenant.objects.create(name="T", domain="t")
    Account.objects.create(tenant=tenant, number="1200", name="AR", account_type="active")
    Account.objects.create(tenant=tenant, number="2200", name="AP", account_type="passive")
    Account.objects.create(tenant=tenant, number="7600", name="Revenue", account_type="income")
    Account.objects.create(tenant=tenant, number="4700", name="VAT Payable", account_type="passive")
    Account.objects.create(
        tenant=tenant, number="1400", name="VAT Receivable", account_type="active"
    )
    Account.objects.create(tenant=tenant, number="4000", name="Expense", account_type="expense")

    post_transaction(
        tenant=tenant,
        event="SALE_INVOICE_POSTED",
        payload={
            "net": Decimal("100"),
            "vat": Decimal("0"),
            "description": "s1",
            "date": date(2024, 4, 1),
        },
    )
    post_transaction(
        tenant=tenant,
        event="SALE_INVOICE_POSTED",
        payload={
            "net": Decimal("50"),
            "vat": Decimal("0"),
            "description": "s2",
            "date": date(2024, 2, 1),
        },
    )
    post_transaction(
        tenant=tenant,
        event="PURCHASE_INVOICE_POSTED",
        payload={
            "net": Decimal("40"),
            "vat": Decimal("0"),
            "description": "p1",
            "date": date(2024, 4, 15),
        },
    )

    pl = pnl_light(tenant=tenant)
    assert pl == {
        "revenue": Decimal("150.00"),
        "expense": Decimal("40.00"),
        "profit": Decimal("110.00"),
    }

    bs = balance_sheet_light(tenant=tenant)
    assert bs == {
        "assets": Decimal("150.00"),
        "liabilities": Decimal("40.00"),
        "equity": Decimal("110.00"),
    }
    assert bs["assets"] == bs["liabilities"] + bs["equity"]

    aging = ar_ap_aging(tenant=tenant, today=date(2024, 5, 1))
    assert aging["ar"]["0-30"] == Decimal("100.00")
    assert aging["ar"]["61-90"] == Decimal("50.00")
    assert aging["ap"]["0-30"] == Decimal("40.00")


@pytest.mark.django_db
def test_related_party_ledger_balances_across_tenants():
    t1 = Tenant.objects.create(name="A", domain="a")
    t2 = Tenant.objects.create(name="B", domain="b")
    for t in (t1, t2):
        Account.objects.create(tenant=t, number="1200", name="AR", account_type="active")
        Account.objects.create(tenant=t, number="2200", name="AP", account_type="passive")
        Account.objects.create(tenant=t, number="4700", name="VAT Payable", account_type="passive")
        Account.objects.create(
            tenant=t, number="1400", name="VAT Receivable", account_type="active"
        )
        Account.objects.create(tenant=t, number="7600", name="Revenue", account_type="income")
        Account.objects.create(tenant=t, number="4000", name="Expense", account_type="expense")

    trace_id = "ICL1"
    post_transaction(
        tenant=t1,
        event="SALE_INVOICE_POSTED",
        payload={
            "net": Decimal("100"),
            "vat": Decimal("0"),
            "description": "s",
            "date": date(2024, 1, 1),
        },
        idempotency_key=f"{trace_id}-A",
    )
    post_transaction(
        tenant=t2,
        event="PURCHASE_INVOICE_POSTED",
        payload={
            "net": Decimal("100"),
            "vat": Decimal("0"),
            "description": "p",
            "date": date(2024, 1, 1),
        },
        idempotency_key=f"{trace_id}-B",
    )

    lines = related_party_ledger(trace_id=trace_id)
    assert len(lines) == 4
    assert {line.tenant for line in lines} == {t1.name, t2.name}
    total_debit = sum(line.debit for line in lines)
    total_credit = sum(line.credit for line in lines)
    assert total_debit == total_credit == Decimal("200.00")
