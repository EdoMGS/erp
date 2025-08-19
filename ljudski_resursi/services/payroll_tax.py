from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings

from ljudski_resursi.services.jls_rates import get_local_rate

Q2 = Decimal("0.01")


@dataclass(frozen=True)
class LocalTaxComputation:
    threshold: Decimal
    lower_rate: Decimal
    higher_rate: Decimal
    base_lower: Decimal
    base_higher: Decimal
    tax_lower: Decimal
    tax_higher: Decimal
    tax_total: Decimal
    jls_source: str


def quant2(x: Decimal) -> Decimal:
    return Decimal(x).quantize(Q2, rounding=ROUND_HALF_UP)


def compute_local_income_tax(*, tenant, employee, payday, taxable_base_eur: Decimal) -> LocalTaxComputation:
    rates = get_local_rate(tenant=tenant, jls_code=getattr(employee, "jls_code", None), payday=payday)
    threshold = Decimal(str(getattr(settings, "MONTHLY_BRACKET_THRESHOLD_EUR", 5000)))
    base = quant2(Decimal(str(taxable_base_eur)))
    base_lower = min(base, threshold)
    base_higher = max(Decimal("0.00"), base - threshold)
    tax_lower = quant2(base_lower * Decimal(str(rates.lower)))
    tax_higher = quant2(base_higher * Decimal(str(rates.higher)))
    total = quant2(tax_lower + tax_higher)
    return LocalTaxComputation(
        threshold=threshold,
        lower_rate=Decimal(str(rates.lower)),
        higher_rate=Decimal(str(rates.higher)),
        base_lower=base_lower,
        base_higher=base_higher,
        tax_lower=tax_lower,
        tax_higher=tax_higher,
        tax_total=total,
        jls_source=rates.source,
    )
