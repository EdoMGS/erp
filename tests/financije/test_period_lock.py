from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from financije.ledger import post_transaction
from financije.models import PeriodClose
from tenants.models import Tenant


@pytest.mark.django_db
def test_period_lock_blocks_posting():
    tenant = Tenant.objects.create(name="T", domain="t.test")
    today = timezone.now().date()
    PeriodClose.objects.create(tenant=tenant, year=today.year, month=today.month)
    with pytest.raises(ValidationError):
        post_transaction(
            tenant=tenant,
            event="SALE_EXPORT",
            payload={"net": Decimal("1.00"), "date": today},
        )
