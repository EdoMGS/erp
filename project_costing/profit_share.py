from decimal import Decimal
from django.db import transaction
from tenants.models import TenantSettings
from .models import ProfitShareRun, ProfitShareParticipant


def run_profit_share(invoice, participant_data, tenant, ref=None):
    """Create ProfitShareRun for given invoice.

    invoice: Invoice instance
    participant_data: iterable of tuples (employee, weight)
    ref: optional reference string
    """
    # tenant explicitly provided; keep function idempotent

    with transaction.atomic():
        existing = ProfitShareRun.objects.filter(invoice=invoice).first()
        if existing:
            return existing

        settings = TenantSettings.objects.filter(tenant=tenant).first()
        ramp_min = settings.ramp_up_min_net if settings else Decimal("800.00")
        total_amount = getattr(invoice, 'amount', Decimal('0'))
        pool_50 = (total_amount * Decimal('0.50')).quantize(Decimal('0.01'))
        pool_30 = (total_amount * Decimal('0.30')).quantize(Decimal('0.01'))
        pool_20 = (total_amount * Decimal('0.20')).quantize(Decimal('0.01'))

        run = ProfitShareRun.objects.create(
            tenant=tenant,
            invoice=invoice,
            ref=ref or str(invoice.invoice_number),
            total_amount=total_amount,
            pool_50=pool_50,
            pool_30=pool_30,
            pool_20=pool_20,
            ramp_up_min_net=ramp_min,
        )

        total_weight = sum(w for _, w in participant_data) or Decimal('0')
        for employee, weight in participant_data:
            share_ratio = weight / total_weight if total_weight else Decimal('0')
            amount_from_30 = (pool_30 * share_ratio).quantize(Decimal('0.01'))
            ramp_adjust = max(ramp_min - amount_from_30, Decimal('0.00'))
            final_amount = amount_from_30 + ramp_adjust
            ProfitShareParticipant.objects.create(
                run=run,
                employee=employee,
                share_weight=weight,
                amount_from_30=amount_from_30,
                ramp_up_adjustment=ramp_adjust,
                final_amount=final_amount,
            )

        return run
