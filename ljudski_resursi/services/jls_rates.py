from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Optional

from django.db.models import Q

from financije.models.tax_local_rate import TaxLocalRate


@dataclass(frozen=True)
class LocalRate:
    lower: Decimal
    higher: Decimal
    source: str


def get_local_rate(*, tenant, jls_code: Optional[str], payday: date) -> LocalRate:
    code = (jls_code or "").strip().upper() or "DEFAULT"
    qs = (
        TaxLocalRate.objects.filter(tenant=tenant, jls_code__in=[code, "DEFAULT"], active=True)
        .filter(valid_from__lte=payday)
        .filter(Q(valid_to__isnull=True) | Q(valid_to__gt=payday))
    )
    prefer = {code: 0, "DEFAULT": 1}
    rec = sorted(qs, key=lambda r: prefer.get(r.jls_code, 2))[:1]
    if rec:
        r = rec[0]
        return LocalRate(lower=r.lower_rate, higher=r.higher_rate, source=r.jls_code)
    return LocalRate(lower=Decimal("0.20"), higher=Decimal("0.30"), source="HARDFALLBACK")
