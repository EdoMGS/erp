"""Central ledger engine with idempotent posting and reversals."""

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .account_map import ACCOUNT_RULES
from .models import Account, JournalEntry, JournalItem


def _resolve_lines(tenant, event: str, payload: dict) -> list[dict]:
    rule = ACCOUNT_RULES.get(event)
    if not rule:
        raise ValueError(f"No posting rule for event {event}")
    return rule(tenant, payload)


@transaction.atomic
def post_transaction(
    *, tenant, event: str, payload: dict, idempotency_key: str | None = None, lock: bool = True
) -> JournalEntry:
    if idempotency_key:
        existing = JournalEntry.objects.filter(
            idempotency_key=idempotency_key, tenant=tenant
        ).first()
        if existing:
            return existing

    lines = _resolve_lines(tenant, event, payload)
    if not lines:
        raise ValueError("Posting produced no lines")

    je = JournalEntry.objects.create(
        tenant=tenant,
        date=(
            payload.get("date")
            or payload.get("issue_date")
            or payload.get("posted_at")
            or payload.get("today")
            or timezone.now().date()
        ),
        description=payload.get("description") or f"Auto post {event}",
        idempotency_key=idempotency_key,
        locked=lock,
    )

    total_debit = Decimal("0.00")
    total_credit = Decimal("0.00")
    for pl in lines:
        acct = Account.objects.get(tenant=tenant, number=pl["account"])
        JournalItem.objects.create(
            tenant=tenant,
            entry=je,
            account=acct,
            debit=pl.get("debit", Decimal("0.00")),
            credit=pl.get("credit", Decimal("0.00")),
        )
        total_debit += pl.get("debit", Decimal("0.00"))
        total_credit += pl.get("credit", Decimal("0.00"))

    if total_debit != total_credit:
        raise ValueError("Unbalanced entry: ΣD != ΣC")

    return je


@transaction.atomic
def reverse_entry(entry: JournalEntry, *, reason: str = "Reversal") -> JournalEntry:
    if entry.locked is False:
        raise ValueError("Only locked entries can be reversed")
    reversal = JournalEntry.objects.create(
        tenant=entry.tenant,
        date=entry.date,
        description=f"Reversal of #{entry.pk}: {reason}",
        reversal_of=entry,
        locked=True,
    )
    for item in JournalItem.objects.filter(entry=entry):
        JournalItem.objects.create(
            tenant=entry.tenant,
            entry=reversal,
            account=item.account,
            debit=item.credit,
            credit=item.debit,
        )
    return reversal
