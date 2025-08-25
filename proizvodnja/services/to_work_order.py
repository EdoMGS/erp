from decimal import Decimal

from django.db import transaction

from inventory.services.reservations import reserve_paint
from proizvodnja.models import RadniNalog


@transaction.atomic
def to_work_order(*, tenant, quote_id: int, option: str, color: str, quantity: Decimal) -> RadniNalog:
    """Create work order if missing and reserve paint using FEFO."""
    wo, created = RadniNalog.objects.get_or_create(
        tenant=tenant, quote_id=quote_id, option=option
    )
    if created:
        reserve_paint(tenant=tenant, work_order=wo, color=color, quantity=quantity)
    return wo
