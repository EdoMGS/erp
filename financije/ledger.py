"""Lightweight tenant-aware double-entry ledger layer bridging to existing accounting models.

Public API:
  post_entry(tenant, lines, ref, memo, date=None) -> JournalEntry (idempotent on tenant+ref)
  trial_balance(tenant) -> list of tuples (account_number, debit, credit, balance)

We reuse financije.models.accounting models and add PostedJournalRef for idempotency.
"""
from __future__ import annotations
from decimal import Decimal, ROUND_HALF_UP
from typing import List, Sequence, Iterable

from django.db import models, transaction
from django.utils import timezone

from financije.models.accounting import Account, JournalEntry, JournalItem, PeriodLock
from financije.models import PostedJournalRef
from tenants.models import Tenant


def money(value) -> Decimal:
    return Decimal(value).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


quantize = money  # backwards compat internal


"""PostedJournalRef model now lives in financije.models.refs (imported above)."""


@transaction.atomic
def _is_locked(tenant: Tenant, date) -> bool:
    return PeriodLock.objects.filter(tenant=tenant, year=date.year, month=date.month).exists()


@transaction.atomic
def post_entry(*, tenant: Tenant, lines: Sequence[dict], ref: str, memo: str, date=None, kind: str = "generic") -> JournalEntry:
    existing_ref = (
        PostedJournalRef.objects.filter(tenant=tenant, ref=ref, kind=kind).select_related("entry").first()
    )
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

    post_date = date or timezone.now().date()
    if _is_locked(tenant, post_date):
        raise ValueError("Period locked for date: %s" % post_date)

    je = JournalEntry.objects.create(
        tenant=tenant,
        date=post_date,
        description=memo,
    )
    JournalItem.objects.bulk_create(
        [
            JournalItem(
                entry=je,
                account=nl["account"],
                debit=nl["debit"],
                credit=nl["credit"],
                cost_center=nl.get("cost_center"),
                labels=nl.get("labels", []),
            )
            for nl in norm_lines
        ]
    )
    PostedJournalRef.objects.create(tenant=tenant, ref=ref, kind=kind, entry=je)
    return je


def trial_balance(tenant: Tenant):
    data = []
    for acct in Account.objects.all():
        debit = acct.journalitem_set.aggregate(models.Sum("debit"))["debit__sum"] or Decimal("0.00")
        credit = acct.journalitem_set.aggregate(models.Sum("credit"))["credit__sum"] or Decimal("0.00")
        # Skip completely inactive OR fully netted (DR==CR) accounts to keep report concise
        if (debit == 0 and credit == 0) or debit == credit:
            continue
        balance = debit - credit
        data.append((acct.number, debit, credit, balance))
    return data


@transaction.atomic
def reverse_entry(*, tenant: Tenant, entry: JournalEntry, ref: str, memo: str | None = None, kind: str = "reversal") -> JournalEntry:
    if entry.tenant_id != tenant.id:
        raise ValueError("Tenant mismatch for reversal")
    memo_final = memo or f"Reversal of JE {entry.id}: {entry.description}"
    lines = []
    for ji in entry.journalitem_set.all():
        dc = "D" if ji.credit and ji.credit > 0 else "C"
        amt = ji.credit if ji.credit > 0 else ji.debit
        if amt == 0:
            continue
        lines.append({
            "account": ji.account,
            "dc": dc,
            "amount": amt,
            "cost_center": ji.cost_center,
            "labels": ji.labels,
        })
    rev = post_entry(
        tenant=tenant,
        lines=lines,
        ref=ref,
        memo=memo_final,
        date=entry.date,
        kind=kind,
    )
    rev.reversal_of = entry
    rev.save(update_fields=["reversal_of"])
    return rev


def is_period_locked(tenant: Tenant, year: int, month: int) -> bool:
    return PeriodLock.objects.filter(tenant=tenant, year=year, month=month).exists()


def close_month(*, tenant: Tenant, year: int, month: int, user=None) -> PeriodLock:
    if is_period_locked(tenant, year, month):
        raise ValueError("Period already locked")
    lock = PeriodLock.objects.create(tenant=tenant, year=year, month=month, closed_by=user)
    return lock


def reopen_month(*, tenant: Tenant, year: int, month: int):
    qs = PeriodLock.objects.filter(tenant=tenant, year=year, month=month)
    if not qs.exists():
        raise ValueError("Period not locked")
    qs.delete()
