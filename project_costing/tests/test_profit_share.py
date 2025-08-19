# project_costing/tests/test_profit_share.py

from decimal import Decimal

import pytest

from project_costing.models import ProfitShareConfig, Project
from tenants.models import Tenant


@pytest.mark.django_db
def test_standard_split():
    tenant = Tenant.objects.create(name="T")
    project = Project.objects.create(name="P", tenant=tenant, start_date="2025-01-01", division="X")
    config = ProfitShareConfig.objects.create(
        project=project,
        company_share=Decimal("50.00"),
        worker_share=Decimal("30.00"),
        dynamic_floor_pct=Decimal("10.00"),
        floor_cap_per_month=Decimal("2000.00"),
    )
    shares = config.calculate_shares(Decimal("10000.00"), is_ramp_up=False)
    assert shares["floor"] == Decimal("1000.00")
    assert shares["worker"] == Decimal("2700.00")
    assert shares["company_after_floor"] == Decimal("6300.00")
    assert shares["fund"] == Decimal("0.00")


@pytest.mark.django_db
def test_ramp_up_split():
    tenant = Tenant.objects.create(name="T")
    project = Project.objects.create(name="P", tenant=tenant, start_date="2025-01-01", division="X")
    config = ProfitShareConfig.objects.create(
        project=project,
        company_share=Decimal("50.00"),
        worker_share=Decimal("30.00"),
        dynamic_floor_pct=Decimal("10.00"),
        floor_cap_per_month=Decimal("2000.00"),
        ramp_up_company_pct=Decimal("40.00"),
        ramp_up_worker_pct=Decimal("40.00"),
        ramp_up_fund_pct=Decimal("20.00"),
    )
    shares = config.calculate_shares(Decimal("10000.00"), is_ramp_up=True)
    assert shares["floor"] == Decimal("1000.00")
    assert shares["worker"] == Decimal("1350.00")
    assert shares["fund"] == Decimal("1350.00")
    assert shares["company_after_floor"] == Decimal("6300.00")


@pytest.mark.django_db
def test_dynamic_floor_cap():
    tenant = Tenant.objects.create(name="T")
    project = Project.objects.create(name="P", tenant=tenant, start_date="2025-01-01", division="X")
    config = ProfitShareConfig.objects.create(
        project=project,
        company_share=Decimal("50.00"),
        worker_share=Decimal("30.00"),
        dynamic_floor_pct=Decimal("10.00"),
        floor_cap_per_month=Decimal("500.00"),  # cap lower than 1000
    )
    shares = config.calculate_shares(Decimal("10000.00"), is_ramp_up=False)
    assert shares["floor"] == Decimal("500.00")
    # remainder = 9500, worker=9500*0.3=2850
    assert shares["worker"] == Decimal("2850.00")
    assert shares["company_after_floor"] == Decimal("6650.00")
    assert shares["fund"] == Decimal("0.00")
