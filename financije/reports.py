from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from django.db.models import Q, Sum
from django.utils import timezone

from .models import Account, JournalItem


@dataclass
class TrialBalanceLine:
    account_number: str
    account_name: str
    account_type: str
    debit: Decimal
    credit: Decimal
    balance: Decimal


def trial_balance(*, tenant, start_date: date | None = None, end_date: date | None = None) -> dict:
    """Compute tenant-scoped trial balance for a date range.

    Returns dict with keys: lines (list[TrialBalanceLine]), total_debit, total_credit.
    """
    qs = JournalItem.objects.filter(tenant=tenant)
    if start_date:
        qs = qs.filter(entry__date__gte=start_date)
    if end_date:
        qs = qs.filter(entry__date__lte=end_date)

    rows = (
        qs.values(
            "account_id",
            "account__number",
            "account__name",
            "account__account_type",
        )
        .annotate(debit=Sum("debit"), credit=Sum("credit"))
        .order_by("account__number")
    )

    lines: list[TrialBalanceLine] = []
    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")
    for r in rows:
        debit = r["debit"] or Decimal("0.00")
        credit = r["credit"] or Decimal("0.00")
        acct_type = r["account__account_type"]
        if acct_type in {"active", "expense"}:
            balance = debit - credit
        else:
            balance = credit - debit
        lines.append(
            TrialBalanceLine(
                account_number=r["account__number"],
                account_name=r["account__name"],
                account_type=acct_type,
                debit=debit,
                credit=credit,
                balance=balance,
            )
        )
        total_debit += debit
        total_credit += credit

    return {
        "lines": lines,
        "total_debit": total_debit,
        "total_credit": total_credit,
    }


@dataclass
class LedgerLine:
    date: date
    description: str
    debit: Decimal
    credit: Decimal
    balance: Decimal


@dataclass
class RelatedPartyLedgerLine:
    tenant: str
    account_number: str
    debit: Decimal
    credit: Decimal


def general_ledger(
    *, tenant, account_number: str, start_date: date | None = None, end_date: date | None = None
) -> dict:
    """Return running ledger for a single account.

    Includes opening balance (as of day before start_date) and lines with running balance.
    """
    try:
        account = Account.objects.get(tenant=tenant, number=account_number)
    except Account.DoesNotExist:
        return {"account": account_number, "opening_balance": Decimal("0.00"), "lines": []}

    base_qs = JournalItem.objects.filter(tenant=tenant, account=account)
    if start_date:
        qs = base_qs.filter(entry__date__gte=start_date)
        # Opening balance up to day before start
        ob_qs = base_qs.filter(entry__date__lt=start_date)
    else:
        qs = base_qs
        ob_qs = base_qs.none()
    if end_date:
        qs = qs.filter(entry__date__lte=end_date)

    debit_sum = ob_qs.aggregate(total=Sum("debit"))["total"] or Decimal("0.00")
    credit_sum = ob_qs.aggregate(total=Sum("credit"))["total"] or Decimal("0.00")
    if account.account_type in {"active", "expense"}:
        opening_balance = debit_sum - credit_sum
    else:
        opening_balance = credit_sum - debit_sum

    rows = (
        qs.select_related("entry")
        .values("entry__date", "entry__description")
        .annotate(debit=Sum("debit"), credit=Sum("credit"))
        .order_by("entry__date", "entry__id")
    )

    lines: list[LedgerLine] = []
    run = opening_balance
    for r in rows:
        debit = r["debit"] or Decimal("0.00")
        credit = r["credit"] or Decimal("0.00")
        if account.account_type in {"active", "expense"}:
            run += debit - credit
        else:
            run += credit - debit
        lines.append(
            LedgerLine(
                date=r["entry__date"],
                description=r["entry__description"],
                debit=debit,
                credit=credit,
                balance=run,
            )
        )

    return {
        "account": account.number,
        "name": account.name,
        "type": account.account_type,
        "opening_balance": opening_balance,
        "lines": lines,
        "closing_balance": run,
    }


def pnl_light(*, tenant) -> dict:
    rows = (
        JournalItem.objects.filter(tenant=tenant)
        .values("account__account_type")
        .annotate(debit=Sum("debit"), credit=Sum("credit"))
    )
    revenue = Decimal("0.00")
    expense = Decimal("0.00")
    for r in rows:
        debit = r["debit"] or Decimal("0.00")
        credit = r["credit"] or Decimal("0.00")
        if r["account__account_type"] == "income":
            revenue += credit - debit
        elif r["account__account_type"] == "expense":
            expense += debit - credit
    return {"revenue": revenue, "expense": expense, "profit": revenue - expense}


def balance_sheet_light(*, tenant) -> dict:
    rows = (
        JournalItem.objects.filter(tenant=tenant)
        .values("account__account_type")
        .annotate(debit=Sum("debit"), credit=Sum("credit"))
    )
    assets = Decimal("0.00")
    liabilities = Decimal("0.00")
    for r in rows:
        debit = r["debit"] or Decimal("0.00")
        credit = r["credit"] or Decimal("0.00")
        if r["account__account_type"] == "active":
            assets += debit - credit
        elif r["account__account_type"] == "passive":
            liabilities += credit - debit
    equity = assets - liabilities
    return {"assets": assets, "liabilities": liabilities, "equity": equity}


def ar_ap_aging(*, tenant, today: date | None = None) -> dict:
    today = today or timezone.now().date()
    buckets = ["0-30", "31-60", "61-90", ">90"]
    ar = {b: Decimal("0.00") for b in buckets}
    ap = {b: Decimal("0.00") for b in buckets}
    items = JournalItem.objects.filter(
        tenant=tenant, account__number__regex=r"^(12|22)"
    ).select_related("entry", "account")
    for item in items:
        days = (today - item.entry.date).days
        if days <= 30:
            bucket = "0-30"
        elif days <= 60:
            bucket = "31-60"
        elif days <= 90:
            bucket = "61-90"
        else:
            bucket = ">90"
        if item.account.number.startswith("12"):
            amount = item.debit - item.credit
            if amount > 0:
                ar[bucket] += amount
        else:
            amount = item.credit - item.debit
            if amount > 0:
                ap[bucket] += amount
    return {"ar": ar, "ap": ap}


def related_party_ledger(*, trace_id: str) -> list[RelatedPartyLedgerLine]:
    rows = (
        JournalItem.objects.filter(entry__idempotency_key__startswith=trace_id)
        .values("tenant__name", "account__number")
        .annotate(debit=Sum("debit"), credit=Sum("credit"))
        .filter(~(Q(debit=0) & Q(credit=0)))
        .order_by("tenant__name", "account__number")
    )
    lines: list[RelatedPartyLedgerLine] = []
    for r in rows:
        lines.append(
            RelatedPartyLedgerLine(
                tenant=r["tenant__name"],
                account_number=r["account__number"],
                debit=r["debit"] or Decimal("0.00"),
                credit=r["credit"] or Decimal("0.00"),
            )
        )
    return lines
