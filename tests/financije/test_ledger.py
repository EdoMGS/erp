from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from financije import account_map_hr as account_map
from financije.ledger import post_transaction, reverse_entry
from financije.models import Account, JournalEntry, JournalItem
from financije.services import load_coa_hr_2025
from tenants.models import Tenant


@pytest.mark.django_db
def test_unbalanced_entry_rejected(monkeypatch):
    tenant = Tenant.objects.create(name="T")
    load_coa_hr_2025(tenant)

    def unbalanced(_tenant, _payload):
        return [
            {"account": "1200", "debit": Decimal("100.00"), "credit": Decimal("0.00")},
            {"account": "7600", "debit": Decimal("0.00"), "credit": Decimal("50.00")},
        ]

    monkeypatch.setitem(account_map.ACCOUNT_RULES, "UNBALANCED", unbalanced)
    with pytest.raises(ValueError):
        post_transaction(tenant=tenant, event="UNBALANCED", payload={})


@pytest.mark.django_db
def test_post_transaction_idempotency():
    tenant = Tenant.objects.create(name="T")
    load_coa_hr_2025(tenant)
    payload = {"net": "100", "vat": "25"}
    je1 = post_transaction(
        tenant=tenant,
        event="SALE_INVOICE_POSTED",
        payload=payload,
        idempotency_key="abc",
    )
    je2 = post_transaction(
        tenant=tenant,
        event="SALE_INVOICE_POSTED",
        payload=payload,
        idempotency_key="abc",
    )
    assert je1.pk == je2.pk
    assert JournalEntry.objects.filter(tenant=tenant).count() == 1


@pytest.mark.django_db
def test_locked_entry_prevents_changes():
    tenant = Tenant.objects.create(name="T")
    load_coa_hr_2025(tenant)
    je = post_transaction(
        tenant=tenant,
        event="SALE_INVOICE_POSTED",
        payload={"net": "100", "vat": "25"},
    )
    assert je.locked

    # Modifying the entry itself should fail
    je.description = "Changed"
    with pytest.raises(ValidationError):
        je.save()

    # Modifying existing journal item should fail
    item = je.journalitem_set.first()
    item.debit += Decimal("1.00")
    with pytest.raises(ValidationError):
        item.save()

    # Adding a new journal item should fail
    bank = Account.objects.get(tenant=tenant, number="1000")
    with pytest.raises(ValidationError):
        JournalItem.objects.create(tenant=tenant, entry=je, account=bank, debit=Decimal("1.00"))


@pytest.mark.django_db
def test_reverse_entry_balanced():
    tenant = Tenant.objects.create(name="T")
    load_coa_hr_2025(tenant)
    je = post_transaction(
        tenant=tenant,
        event="SALE_INVOICE_POSTED",
        payload={"net": "100", "vat": "25"},
    )
    rev = reverse_entry(je)
    assert rev.locked
    assert rev.is_balanced()
    orig = list(
        je.journalitem_set.order_by("account__number").values_list(
            "account__number", "debit", "credit"
        )
    )
    rev_items = list(
        rev.journalitem_set.order_by("account__number").values_list(
            "account__number", "debit", "credit"
        )
    )
    assert orig
    assert len(orig) == len(rev_items)
    for (acct, d, c), (acct_r, d_r, c_r) in zip(orig, rev_items, strict=False):
        assert acct == acct_r
        assert d == c_r
        assert c == d_r
