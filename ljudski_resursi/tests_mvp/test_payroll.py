import pytest
from decimal import Decimal
from ljudski_resursi.models import LocationConfig
from ljudski_resursi.services import PayrollCalculator

pytestmark = pytest.mark.skip(reason="Skipped in MVP: payroll logic under refactor")


@pytest.mark.django_db
def test_payroll_calculation():
    config = LocationConfig.objects.create(
        location_name="Bakar",
        gross_minimal=Decimal("951.72"),
        net_minimal=Decimal("750.00"),
        employer_contrib_pct=Decimal("16.5"),
        meal_allowance_monthly=Decimal("100.00"),
        housing_allowance_monthly=Decimal("600.00"),
        worker_share=Decimal("30.00"),
    )

    invoice_amount = Decimal("5000.00")
    result = PayrollCalculator.compute(invoice_amount, config)

    # Calculation: 951.72 + 16.5% employer contrib = 1108.75
    assert result["minimal_wage"] == Decimal("1108.75")
    assert result["allowances"] == Decimal("700.00")
    # worker_pool = 5000 * 0.30 = 1500; bonus = 1500 - (1108.75 + 700) = negative => 0.00
    assert result["bonus_pool"] == Decimal("0.00")


@pytest.mark.django_db
def test_payroll_no_bonus_for_low_invoice():
    # Invoice amount too low to cover minimal wage + allowances
    config = LocationConfig.objects.create(
        location_name="Bakar",
        gross_minimal=Decimal("951.72"),
        net_minimal=Decimal("750.00"),
        employer_contrib_pct=Decimal("16.5"),
        meal_allowance_monthly=Decimal("100.00"),
        housing_allowance_monthly=Decimal("600.00"),
        worker_share=Decimal("30.00"),
    )
    invoice_amount = Decimal("1000.00")
    result = PayrollCalculator.compute(invoice_amount, config)
    # minimal_wage = gross_minimal + employer contributions = 951.72 + 157.03 = 1108.75
    assert result["minimal_wage"] == Decimal("1108.75")
    # allowances = meal + housing = 100 + 600
    assert result["allowances"] == Decimal("700.00")
    # worker_pool = 1000 * 0.3 = 300, less than minimal_wage + allowances => no bonus
    assert result["bonus_pool"] == Decimal("0.00")
