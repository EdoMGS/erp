from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from financije.services.posting_rules import profit_share_distribution
from project_costing.pdf.profit_share import render_profit_share_pdf


@dataclass
class ProfitShareResult:
    base: Decimal
    company: Decimal
    workers: Decimal
    owner: Decimal
    rounding_diff: Decimal
    entry_id: int
    pdf: bytes


def calculate_profit_share(*, tenant, net: Decimal, vat: Decimal = Decimal("0"), idempotency_key: str | None = None) -> ProfitShareResult:
    """Distribute profit 50/30/20 and post journal entry.

    Base for distribution is NET for VAT registered tenants, otherwise GROSS.
    """
    gross = net + vat
    base = net if getattr(tenant, "is_vat_registered", False) else gross

    company = (base * Decimal("0.50")).quantize(Decimal("0.01"))
    workers = (base * Decimal("0.30")).quantize(Decimal("0.01"))
    owner = (base * Decimal("0.20")).quantize(Decimal("0.01"))
    total = company + workers + owner
    diff = base - total

    entry = profit_share_distribution(tenant=tenant, base=base, company=company, workers=workers, owner=owner, rounding_diff=diff, idempotency_key=idempotency_key)

    pdf = render_profit_share_pdf(base=base, company=company, workers=workers, owner=owner, rounding_diff=diff)

    return ProfitShareResult(
        base=base,
        company=company,
        workers=workers,
        owner=owner,
        rounding_diff=diff,
        entry_id=entry.pk,
        pdf=pdf,
    )
