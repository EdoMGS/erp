"""Central ledger engine with idempotent posting and reversals."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .account_map_hr import ACCOUNT_RULES
from .models import Account, JournalEntry, JournalItem, PeriodClose


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

    # K3 safeguard: block postings into closed periods
    post_date = (
        payload.get("date")
        or payload.get("issue_date")
        or payload.get("posted_at")
        or payload.get("today")
        or timezone.now().date()
    )
    if PeriodClose.objects.filter(
        tenant=tenant, year=post_date.year, month=post_date.month
    ).exists():
        period_key = f"{post_date.year:04d}-{post_date.month:02d}"
        raise ValidationError(f"Period {period_key} is closed. Use reversal.")

    # Create entry unlocked first so items can be added
    je = JournalEntry.objects.create(
        tenant=tenant,
        date=post_date,
        description=payload.get("description") or f"Auto post {event}",
        idempotency_key=idempotency_key,
        locked=False,
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

    if lock:
        now = timezone.now()
        JournalEntry.objects.filter(pk=je.pk).update(locked=True, posted_at=now)
        je.locked = True
        je.posted_at = now

    return je


@transaction.atomic
def reverse_entry(entry: int | JournalEntry, *, reason: str = "Reversal") -> JournalEntry:
    """Create a full reversal for the given locked entry."""
    if not isinstance(entry, JournalEntry):
        entry = JournalEntry.objects.get(pk=entry)
    if entry.locked is False:
        raise ValueError("Only locked entries can be reversed")

    reversal = JournalEntry.objects.create(
        tenant=entry.tenant,
        date=entry.date,
        description=f"Reversal of #{entry.pk}: {reason}",
        reversal_of=entry,
        locked=False,
    )

    for item in JournalItem.objects.filter(entry=entry):
        JournalItem.objects.create(
            tenant=entry.tenant,
            entry=reversal,
            account=item.account,
            debit=item.credit,
            credit=item.debit,
        )

    now = timezone.now()
    JournalEntry.objects.filter(pk=reversal.pk).update(locked=True, posted_at=now)
    reversal.locked = True
    reversal.posted_at = now

    return reversal
