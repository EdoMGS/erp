from decimal import Decimal

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from project_costing.models import (
    CostLine,
    LabourEntry,
    ProfitShareConfig,
    Project,
    WorkerShare,
)
from tenants.models import Tenant


@pytest.mark.django_db
def test_profit_share_positive():
    tenant = Tenant.objects.create(name="TestTenant")
    user1 = get_user_model().objects.create(username="worker1")
    user2 = get_user_model().objects.create(username="worker2")
    project = Project.objects.create(
        tenant=tenant,
        name="P1",
        start_date=timezone.now(),
        revenue=Decimal("1000.00"),
        division="BRAVARIJA",
    )
    CostLine.objects.create(project=project, type="MAT", description="mat1", amount=Decimal("400.00"))
    LabourEntry.objects.create(project=project, worker=user1, hours=5, date=timezone.now())
    LabourEntry.objects.create(project=project, worker=user2, hours=3, date=timezone.now())
    ProfitShareConfig.objects.create(
        project=project,
        owner_share=Decimal("20.00"),
        worker_share=Decimal("30.00"),
        company_share=Decimal("50.00"),
    )
    # Trigger signal
    project.save()
    shares = WorkerShare.objects.filter(project=project)
    assert shares.count() == 2
    total_worker_share = sum(ws.amount for ws in shares)
    assert total_worker_share == pytest.approx(Decimal("180.00"))  # 30% of 600 profit


@pytest.mark.django_db
def test_profit_share_zero_or_negative():
    tenant = Tenant.objects.create(name="TestTenant2")
    user = get_user_model().objects.create(username="worker3")
    project = Project.objects.create(
        tenant=tenant,
        name="P2",
        start_date=timezone.now(),
        revenue=Decimal("100.00"),
        division="FARBANJE",
    )
    CostLine.objects.create(project=project, type="MAT", description="mat2", amount=Decimal("150.00"))
    LabourEntry.objects.create(project=project, worker=user, hours=2, date=timezone.now())
    ProfitShareConfig.objects.create(
        project=project,
        owner_share=Decimal("20.00"),
        worker_share=Decimal("30.00"),
        company_share=Decimal("50.00"),
    )
    # Trigger signal
    project.save()
    shares = WorkerShare.objects.filter(project=project)
    assert shares.count() == 0
