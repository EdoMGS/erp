import pytest
from decimal import Decimal
from financije.ledger import post_entry, reverse_entry, trial_balance, close_month, PostedJournalRef
from financije.models import JournalEntry
from tenants.models import Tenant

pytestmark = pytest.mark.django_db


@pytest.fixture()
def tenant():
    return Tenant.objects.create(name="T")


def test_post_entry_idempotent(tenant):
    je1 = post_entry(tenant=tenant, ref="X1", kind="invoice", memo="M", lines=[
        {"account": "400", "dc": "C", "amount": "10"},
        {"account": "120", "dc": "D", "amount": "10"},
    ])
    je2 = post_entry(tenant=tenant, ref="X1", kind="invoice", memo="M again", lines=[
        {"account": "400", "dc": "C", "amount": "10"},
        {"account": "120", "dc": "D", "amount": "10"},
    ])
    assert je1.id == je2.id
    assert PostedJournalRef.objects.filter(tenant=tenant, ref="X1", kind="invoice").count() == 1


def test_reversal_and_trial_balance_collapse(tenant):
    je = post_entry(tenant=tenant, ref="INV2", kind="invoice", memo="Invoice", lines=[
        {"account": "400", "dc": "C", "amount": "100"},
        {"account": "120", "dc": "D", "amount": "100"},
    ])
    rev = reverse_entry(tenant=tenant, entry=je, ref="INV2-R")
    assert rev.reversal_of_id == je.id
    tb = trial_balance(tenant)
    # Both accounts should be filtered out after reversal (netted)
    assert tb == []


def test_period_lock_blocks_posting(tenant):
    je = post_entry(tenant=tenant, ref="L1", kind="invoice", memo="Invoice", lines=[
        {"account": "400", "dc": "C", "amount": "50"},
        {"account": "120", "dc": "D", "amount": "50"},
    ])
    close_month(tenant=tenant, year=je.date.year, month=je.date.month)
    with pytest.raises(ValueError):
        post_entry(tenant=tenant, ref="AFTER", kind="invoice", memo="After lock", date=je.date, lines=[
            {"account": "400", "dc": "C", "amount": "5"},
            {"account": "120", "dc": "D", "amount": "5"},
        ])


def test_reverse_cross_tenant_guard(tenant):
    other = Tenant.objects.create(name="O")
    je = post_entry(tenant=tenant, ref="INV3", kind="invoice", memo="Invoice", lines=[
        {"account": "400", "dc": "C", "amount": "30"},
        {"account": "120", "dc": "D", "amount": "30"},
    ])
    with pytest.raises(ValueError):
        reverse_entry(tenant=other, entry=je, ref="INV3-R")
