from decimal import Decimal

import pytest

from financije.models import Account, JournalEntry, JournalItem
from project_costing.services.profit_share import calculate_profit_share
from tenants.models import Tenant


@pytest.fixture
def tenant_with_accounts(db):
    tenant = Tenant.objects.create(name="T", domain="t")
    tenant.is_vat_registered = True
    Account.objects.create(tenant=tenant, number="7600", name="Cost", account_type="expense")
    Account.objects.create(tenant=tenant, number="2600", name="Liab1", account_type="passive")
    Account.objects.create(tenant=tenant, number="2601", name="Liab2", account_type="passive")
    Account.objects.create(tenant=tenant, number="8400", name="Equity", account_type="passive")
    Account.objects.create(tenant=tenant, number="4999", name="Diff", account_type="expense")
    return tenant


@pytest.mark.django_db
def test_distribution_sums_to_base(tenant_with_accounts):
    result = calculate_profit_share(
        tenant=tenant_with_accounts, net=Decimal("100.00"), vat=Decimal("25.00")
    )
    assert result.base == result.company + result.workers + result.owner + result.rounding_diff


@pytest.mark.django_db
def test_posts_balanced_journal(tenant_with_accounts):
    res = calculate_profit_share(
        tenant=tenant_with_accounts, net=Decimal("100.00"), vat=Decimal("25.00")
    )
    je = JournalEntry.objects.get(pk=res.entry_id)
    assert je.total_debit == je.total_credit == res.base


@pytest.mark.django_db
def test_rounding_diff_captured_on_4999():
    tenant = Tenant.objects.create(name="T2", domain="t2")
    tenant.is_vat_registered = True
    Account.objects.create(tenant=tenant, number="7600", name="Cost", account_type="expense")
    Account.objects.create(tenant=tenant, number="2600", name="Liab1", account_type="passive")
    Account.objects.create(tenant=tenant, number="2601", name="Liab2", account_type="passive")
    Account.objects.create(tenant=tenant, number="8400", name="Equity", account_type="passive")
    diff_acct = Account.objects.create(tenant=tenant, number="4999", name="Diff", account_type="expense")

    res = calculate_profit_share(tenant=tenant, net=Decimal("0.03"), vat=Decimal("0"))
    assert res.rounding_diff != Decimal("0.00")
    ji = JournalItem.objects.get(entry_id=res.entry_id, account=diff_acct)
    assert ji.debit == abs(res.rounding_diff) or ji.credit == abs(res.rounding_diff)
