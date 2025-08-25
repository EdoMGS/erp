from datetime import date
from decimal import Decimal

import pytest

from financije.ledger import post_transaction
from financije.models import Account
from financije.reports import ar_ap_aging
from tenants.models import Tenant


@pytest.mark.django_db
def test_ar_ap_aging_all_buckets():
    tenant = Tenant.objects.create(name="T", domain="t")
    Account.objects.create(tenant=tenant, number="1200", name="AR", account_type="active")
    Account.objects.create(tenant=tenant, number="2200", name="AP", account_type="passive")
    Account.objects.create(tenant=tenant, number="7600", name="Revenue", account_type="income")
    Account.objects.create(tenant=tenant, number="4700", name="VAT Payable", account_type="passive")
    Account.objects.create(
        tenant=tenant, number="1400", name="VAT Receivable", account_type="active"
    )
    Account.objects.create(tenant=tenant, number="4000", name="Expense", account_type="expense")

    # AR buckets
    post_transaction(
        tenant=tenant,
        event="SALE_INVOICE_POSTED",
        payload={
            "net": Decimal("100"),
            "vat": Decimal("0"),
            "description": "ar1",
            "date": date(2024, 4, 25),
        },
    )
    post_transaction(
        tenant=tenant,
        event="SALE_INVOICE_POSTED",
        payload={
            "net": Decimal("200"),
            "vat": Decimal("0"),
            "description": "ar2",
            "date": date(2024, 3, 25),
        },
    )
    post_transaction(
        tenant=tenant,
        event="SALE_INVOICE_POSTED",
        payload={
            "net": Decimal("300"),
            "vat": Decimal("0"),
            "description": "ar3",
            "date": date(2024, 1, 20),
        },
    )

    # AP buckets
    post_transaction(
        tenant=tenant,
        event="PURCHASE_INVOICE_POSTED",
        payload={
            "net": Decimal("400"),
            "vat": Decimal("0"),
            "description": "ap1",
            "date": date(2024, 4, 10),
        },
    )
    post_transaction(
        tenant=tenant,
        event="PURCHASE_INVOICE_POSTED",
        payload={
            "net": Decimal("500"),
            "vat": Decimal("0"),
            "description": "ap2",
            "date": date(2024, 2, 20),
        },
    )
    post_transaction(
        tenant=tenant,
        event="PURCHASE_INVOICE_POSTED",
        payload={
            "net": Decimal("600"),
            "vat": Decimal("0"),
            "description": "ap3",
            "date": date(2024, 1, 10),
        },
    )

    aging = ar_ap_aging(tenant=tenant, today=date(2024, 5, 1))
    assert aging["ar"]["0-30"] == Decimal("100.00")
    assert aging["ar"]["31-60"] == Decimal("200.00")
    assert aging["ar"]["61-90"] == Decimal("0.00")
    assert aging["ar"][">90"] == Decimal("300.00")
    assert aging["ap"]["0-30"] == Decimal("400.00")
    assert aging["ap"]["31-60"] == Decimal("0.00")
    assert aging["ap"]["61-90"] == Decimal("500.00")
    assert aging["ap"][">90"] == Decimal("600.00")
