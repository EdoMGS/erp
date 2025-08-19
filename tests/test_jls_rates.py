from datetime import date
from decimal import Decimal

import pytest

from financije.models.tax_local_rate import TaxLocalRate
from ljudski_resursi.services.jls_rates import get_local_rate

pytestmark = pytest.mark.django_db


@pytest.fixture()
def tenant():
    from tenants.models import Tenant
    return Tenant.objects.create(name="Demo")


def seed(tenant):
    TaxLocalRate.objects.bulk_create(
        [
            TaxLocalRate(tenant=tenant, jls_code="DEFAULT", name="Default", lower_rate="0.20", higher_rate="0.30", valid_from=date(2024, 1, 1)),
            TaxLocalRate(tenant=tenant, jls_code="RIJEKA", name="Rijeka", lower_rate="0.22", higher_rate="0.32", valid_from=date(2025, 1, 1)),
            TaxLocalRate(tenant=tenant, jls_code="ZAGREB", name="Zagreb", lower_rate="0.23", higher_rate="0.33", valid_from=date(2025, 3, 1)),
            TaxLocalRate(tenant=tenant, jls_code="BAKAR", name="Bakar", lower_rate="0.20", higher_rate="0.30", valid_from=date(2024, 1, 1)),
            TaxLocalRate(tenant=tenant, jls_code="KRALJEVICA", name="Kraljevica", lower_rate="0.20", higher_rate="0.30", valid_from=date(2024, 1, 1)),
        ]
    )


def test_rate_fallback_default(tenant):
    seed(tenant)
    r = get_local_rate(tenant=tenant, jls_code="", payday=date(2024, 6, 1))
    assert r.lower == Decimal("0.20") and r.higher == Decimal("0.30") and r.source in {"DEFAULT", "HARDFALLBACK"}


def test_rate_rijeka_after_2025(tenant):
    seed(tenant)
    r = get_local_rate(tenant=tenant, jls_code="RIJEKA", payday=date(2025, 6, 1))
    assert r.lower == Decimal("0.22") and r.higher == Decimal("0.32") and r.source == "RIJEKA"


def test_rate_zagreb_cutover(tenant):
    seed(tenant)
    r_before = get_local_rate(tenant=tenant, jls_code="ZAGREB", payday=date(2025, 2, 15))
    assert r_before.lower == Decimal("0.20") and r_before.higher == Decimal("0.30")
    r_after = get_local_rate(tenant=tenant, jls_code="ZAGREB", payday=date(2025, 3, 2))
    assert r_after.lower == Decimal("0.23") and r_after.higher == Decimal("0.33")
