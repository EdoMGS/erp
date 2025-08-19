from decimal import Decimal
import pytest
from django.utils import timezone

from financije.ledger import post_entry, trial_balance, reverse_entry
from financije.models import Account
from tenants.models import Tenant


@pytest.mark.django_db
def test_trial_balance_is_tenant_scoped():
    tenant_a = Tenant.objects.create(name="Tenant A")
    tenant_b = Tenant.objects.create(name="Tenant B")
    rev_acct = Account.objects.get(number="400")
    cash = Account.objects.get(number="120")

    today = timezone.now().date()

    post_entry(
        tenant=tenant_a,
        ref="A1",
        memo="Revenue A",
        lines=[
            {"account": rev_acct, "dc": "C", "amount": Decimal("100.00")},
            {"account": cash, "dc": "D", "amount": Decimal("100.00")},
        ],
        date=today,
    )
    post_entry(
        tenant=tenant_b,
        ref="B1",
        memo="Revenue B",
        lines=[
            {"account": rev_acct, "dc": "C", "amount": Decimal("300.00")},
            {"account": cash, "dc": "D", "amount": Decimal("300.00")},
        ],
        date=today,
    )

    tb_a = {a: (d, c, b) for a, d, c, b in trial_balance(tenant_a)}
    tb_b = {a: (d, c, b) for a, d, c, b in trial_balance(tenant_b)}

    assert tb_a["400"][1] == Decimal("100.00")  # credit amount for tenant A
    assert tb_b["400"][1] == Decimal("300.00")  # credit amount for tenant B
    assert tb_a["400"][1] != tb_b["400"][1]


@pytest.mark.django_db
def test_reverse_entry_affects_single_tenant():
    tenant = Tenant.objects.create(name="Tenant Solo")
    rev_acct = Account.objects.get(number="400")
    cash = Account.objects.get(number="120")
    today = timezone.now().date()

    je = post_entry(
        tenant=tenant,
        ref="REV1",
        memo="Revenue",
        lines=[
            {"account": rev_acct, "dc": "C", "amount": Decimal("200.00")},
            {"account": cash, "dc": "D", "amount": Decimal("200.00")},
        ],
        date=today,
    )
    reverse_entry(tenant=tenant, entry=je, ref="REV1-R")

    tb = trial_balance(tenant)
    # All movements net to zero so list should be empty (show_netted False default)
    assert tb == []
