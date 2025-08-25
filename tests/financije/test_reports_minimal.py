from datetime import date
from decimal import Decimal

import pytest

from financije.ledger import post_transaction
from financije.models import Account
from financije.reports import ar_ap_aging, balance_sheet_light, pnl_light
from tenants.models import Tenant


@pytest.mark.django_db
def test_reports_compute_expected_values():
    tenant = Tenant.objects.create(name="T", domain="t")
    Account.objects.create(tenant=tenant, number="120", name="AR", account_type="active")
    Account.objects.create(tenant=tenant, number="220", name="AP", account_type="passive")
    Account.objects.create(tenant=tenant, number="400", name="Revenue", account_type="income")
    Account.objects.create(tenant=tenant, number="470", name="VAT Payable", account_type="passive")
    Account.objects.create(
        tenant=tenant, number="471", name="VAT Receivable", account_type="active"
    )
    Account.objects.create(tenant=tenant, number="500", name="Expense", account_type="expense")

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

    aging = ar_ap_aging(tenant=tenant, today=date(2024, 5, 1))
    assert aging["ar"]["0-30"] == Decimal("100.00")
    assert aging["ar"]["61-90"] == Decimal("50.00")
    assert aging["ap"]["0-30"] == Decimal("40.00")
