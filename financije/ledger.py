"""Lightweight tenant-aware double-entry ledger layer bridging to existing accounting models.

Public API:
  post_entry(tenant, lines, ref, memo, date=None) -> JournalEntry (idempotent on tenant+ref)
  trial_balance(tenant) -> list of tuples (account_number, debit, credit, balance)

We reuse financije.models.accounting models and add PostedJournalRef for idempotency.
"""
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Sequence

from django.db import models, transaction
from django.utils import timezone

from financije.models.accounting import Account, JournalEntry, JournalItem
from tenants.models import Tenant


def quantize(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class PostedJournalRef(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    ref = models.CharField(max_length=64)
    entry = models.OneToOneField(JournalEntry, on_delete=models.CASCADE, related_name="posted_ref")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("tenant", "ref")


@transaction.atomic
def post_entry(*, tenant: Tenant, lines: Sequence[dict], ref: str, memo: str, date=None) -> JournalEntry:
    existing_ref = PostedJournalRef.objects.filter(tenant=tenant, ref=ref).select_related("entry").first()
    if existing_ref:
        return existing_ref.entry

    debit_total = Decimal("0")
    credit_total = Decimal("0")
    norm_lines: List[dict] = []
    for ln in lines:
        amt = quantize(Decimal(ln["amount"]))
        if amt == 0:
            continue
        dc = ln["dc"].upper()
        acct = ln["account"]
        if isinstance(acct, str):
            acct_obj = Account.objects.filter(number=acct).first()
        else:
            acct_obj = acct
        if not acct_obj:
            raise ValueError(f"Account not found: {ln['account']}")
        if dc == "D":
            debit_total += amt
            norm_lines.append({"account": acct_obj, "debit": amt, "credit": Decimal("0")})
        elif dc == "C":
            credit_total += amt
            norm_lines.append({"account": acct_obj, "debit": Decimal("0"), "credit": amt})
        else:
            raise ValueError("dc must be 'D' or 'C'")

    if debit_total != credit_total:
        raise ValueError("Entry not balanced (DR != CR)")

    je = JournalEntry.objects.create(
        date=date or timezone.now().date(),
        description=memo,
    )
    JournalItem.objects.bulk_create(
        [JournalItem(entry=je, account=nl["account"], debit=nl["debit"], credit=nl["credit"]) for nl in norm_lines]
    )
    PostedJournalRef.objects.create(tenant=tenant, ref=ref, entry=je)
    return je


def trial_balance(tenant: Tenant):
    data = []
    for acct in Account.objects.all():
        debit = acct.journalitem_set.aggregate(models.Sum("debit"))["debit__sum"] or Decimal("0.00")
        credit = acct.journalitem_set.aggregate(models.Sum("credit"))["credit__sum"] or Decimal("0.00")
        if debit == 0 and credit == 0:
            continue
        balance = debit - credit
        data.append((acct.number, debit, credit, balance))
    return data
