from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction

from financije.ledger import post_entry, quantize
from tenants.models import TenantSettings

from .models import ProfitShareParticipant, ProfitShareRun


def _basis(invoice, tenant):  # noqa: D401
    """Return profit-share basis.

    Uses invoice.total_base when tenant is VAT registered and tax > 0 else falls back to total_amount.
    Backwards compatibility: falls back to legacy 'amount' attr if new totals missing.
    """
    total_base = getattr(invoice, 'total_base', None)
    total_tax = getattr(invoice, 'total_tax', None)
    total_amount = getattr(invoice, 'total_amount', None)
    if (
        hasattr(tenant, 'vat_registered')
        and tenant.vat_registered
        and total_tax is not None
        and total_base is not None
        and total_tax > 0
    ):
        return quantize(total_base)
    # Fallback order: total_amount -> amount -> 0
    if total_amount is not None:
        return quantize(total_amount)
    legacy_amount = getattr(invoice, 'amount', Decimal('0'))
    return quantize(legacy_amount)


def run_profit_share(invoice, participant_data, tenant, ref=None):
    """Compute and post profit-share (50/30/20) returning ProfitShareRun.

    Idempotent by invoice.
    """
    ref_key = ref or f"PS-{invoice.invoice_number}"
    with transaction.atomic():
        existing = ProfitShareRun.objects.filter(invoice=invoice).first()
        if existing:
            return existing

        settings = TenantSettings.objects.filter(tenant=tenant).first()
        ramp_min = settings.ramp_up_min_net if settings else Decimal("800.00")

        basis = _basis(invoice, tenant)
        # Pools
        pool_50_raw = basis * Decimal('0.50')
        pool_30_raw = basis * Decimal('0.30')
        pool_20_raw = basis * Decimal('0.20')
        pool_50 = quantize(pool_50_raw)
        pool_30 = quantize(pool_30_raw)
        pool_20 = quantize(pool_20_raw)
        rounding_diff = quantize(basis - (pool_50 + pool_30 + pool_20))

        run = ProfitShareRun.objects.create(
            tenant=tenant,
            invoice=invoice,
            ref=ref_key,
            total_amount=basis,
            pool_50=pool_50,
            pool_30=pool_30,
            pool_20=pool_20,
            ramp_up_min_net=ramp_min,
            rounding_diff=rounding_diff,
        )

        total_weight = sum(w for _, w in participant_data) or Decimal('0')
        allocations = []
        if total_weight > 0:
            for employee, weight in participant_data:
                ratio = weight / total_weight
                base_amt = quantize(pool_30 * ratio)
                ramp_adj = max(ramp_min - base_amt, Decimal('0.00'))
                final_amt = quantize(base_amt + ramp_adj)
                allocations.append((employee, weight, base_amt, ramp_adj, final_amt))

        # Rounding diff allocation to first participant if needed
        alloc_sum = sum(a[2] for a in allocations)
        diff_line = quantize(pool_30 - alloc_sum)
        if allocations and diff_line != 0:
            first = allocations[0]
            allocations[0] = (first[0], first[1], quantize(first[2] + diff_line), first[3], quantize(first[4] + diff_line))

        for employee, weight, amount_from_30, ramp_adj, final_amt in allocations:
            ProfitShareParticipant.objects.create(
                run=run,
                employee=employee,
                share_weight=weight,
                amount_from_30=amount_from_30,
                ramp_up_adjustment=ramp_adj,
                final_amount=final_amt,
            )

        # Ledger postings (30% expense/liability, 20% expense/equity; 50% no posting now)
        if settings:
            lines = []
            total_liability = quantize(sum((a[4] for a in allocations), Decimal('0.00')))
            if total_liability > 0:
                lines.append({'account': settings.acc_profit_share_expense, 'dc': 'D', 'amount': total_liability})
                lines.append({'account': settings.acc_profit_share_liability, 'dc': 'C', 'amount': total_liability})
            if pool_20 > 0:
                lines.append({'account': settings.acc_profit_share_expense, 'dc': 'D', 'amount': pool_20})
                lines.append({'account': settings.acc_profit_share_equity, 'dc': 'C', 'amount': pool_20})
            if rounding_diff != 0:
                amt = abs(rounding_diff)
                if rounding_diff > 0:
                    lines.append({'account': settings.acc_rounding_diff, 'dc': 'D', 'amount': amt})
                    lines.append({'account': settings.acc_profit_share_equity, 'dc': 'C', 'amount': amt})
                else:
                    lines.append({'account': settings.acc_rounding_diff, 'dc': 'C', 'amount': amt})
                    lines.append({'account': settings.acc_profit_share_expense, 'dc': 'D', 'amount': amt})
            if lines:
                try:
                    je = post_entry(tenant=tenant, lines=lines, ref=f"PSLED-{ref_key}", memo=f"Profit share {invoice.invoice_number}")
                    run.posted_entry_id = getattr(je, 'id', None)
                    run.save(update_fields=['posted_entry_id'])
                except Exception:
                    pass

        return run
