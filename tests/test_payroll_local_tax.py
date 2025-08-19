from datetime import date
from decimal import Decimal

import pytest

from financije.models.tax_local_rate import TaxLocalRate
from ljudski_resursi.services.payroll_tax import compute_local_income_tax

pytestmark = pytest.mark.django_db


@pytest.fixture()
def tenant():
    from tenants.models import Tenant
    return Tenant.objects.create(name="Demo")


def seed_rates(tenant):
    TaxLocalRate.objects.bulk_create(
        [
            TaxLocalRate(tenant=tenant, jls_code="DEFAULT", name="Default", lower_rate="0.20", higher_rate="0.30", valid_from=date(2024, 1, 1)),
            TaxLocalRate(tenant=tenant, jls_code="RIJEKA", name="Rijeka", lower_rate="0.22", higher_rate="0.32", valid_from=date(2025, 1, 1)),
            TaxLocalRate(tenant=tenant, jls_code="BAKAR", name="Bakar", lower_rate="0.20", higher_rate="0.30", valid_from=date(2024, 1, 1)),
            TaxLocalRate(tenant=tenant, jls_code="ZAGREB", name="Zagreb", lower_rate="0.23", higher_rate="0.33", valid_from=date(2025, 3, 1)),
        ]
    )


class DummyEmp:
    def __init__(self, code):
        self.jls_code = code


def test_rijeka_7k_base(tenant, settings):
    seed_rates(tenant)
    settings.MONTHLY_BRACKET_THRESHOLD_EUR = 5000
    emp = DummyEmp("RIJEKA")
    comp = compute_local_income_tax(tenant=tenant, employee=emp, payday=date(2025, 6, 1), taxable_base_eur=Decimal("7000"))
    assert comp.tax_lower == Decimal("1100.00")  # 22% * 5000
    assert comp.tax_higher == Decimal("640.00")  # 32% * 2000
    assert comp.tax_total == Decimal("1740.00")


def test_bakar_7k_base(tenant, settings):
    seed_rates(tenant)
    settings.MONTHLY_BRACKET_THRESHOLD_EUR = 5000
    emp = DummyEmp("BAKAR")
    comp = compute_local_income_tax(tenant=tenant, employee=emp, payday=date(2025, 6, 1), taxable_base_eur=Decimal("7000"))
    assert comp.tax_total == Decimal("1600.00")  # 1000 + 600


def test_zagreb_cutover_before_after(tenant, settings):
    seed_rates(tenant)
    settings.MONTHLY_BRACKET_THRESHOLD_EUR = 5000
    emp = DummyEmp("ZAGREB")
    comp_before = compute_local_income_tax(tenant=tenant, employee=emp, payday=date(2025, 2, 20), taxable_base_eur=Decimal("6000"))
    assert comp_before.tax_total == Decimal("1300.00")
    comp_after = compute_local_income_tax(tenant=tenant, employee=emp, payday=date(2025, 3, 5), taxable_base_eur=Decimal("6000"))
    assert comp_after.tax_total == Decimal("1480.00")
