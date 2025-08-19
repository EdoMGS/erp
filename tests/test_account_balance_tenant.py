from decimal import Decimal
import pytest
from django.utils import timezone

from financije.ledger import post_entry
from financije.models import Account
from tenants.models import Tenant


@pytest.mark.django_db
def test_account_balance_for_tenant_helper():
    t1 = Tenant.objects.create(name="T1")
    t2 = Tenant.objects.create(name="T2")
    rev = Account.objects.get(number="400")
    cash = Account.objects.get(number="120")
    today = timezone.now().date()

    post_entry(
        tenant=t1,
        ref="T1-1",
        memo="Rev1",
        lines=[
            {"account": rev, "dc": "C", "amount": Decimal("150.00")},
            {"account": cash, "dc": "D", "amount": Decimal("150.00")},
        ],
        date=today,
    )
    post_entry(
        tenant=t2,
        ref="T2-1",
        memo="Rev2",
        lines=[
            {"account": rev, "dc": "C", "amount": Decimal("90.00")},
            {"account": cash, "dc": "D", "amount": Decimal("90.00")},
        ],
        date=today,
    )

    bal_t1 = rev.balance_for_tenant(t1)
    bal_t2 = rev.balance_for_tenant(t2)

    assert bal_t1 != bal_t2
    assert bal_t1 < 0 or bal_t1 > 0  # just ensure numeric
