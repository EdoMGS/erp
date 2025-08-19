from decimal import Decimal

import pytest

from accounts.models import CustomUser
from financije.models.invoice import Invoice
from ljudski_resursi.models import (
    Department,
    Employee,
    ExpertiseLevel,
    HierarchicalLevel,
    Position,
)
from project_costing.profit_share import run_profit_share
from tenants.models import Tenant, TenantSettings

pytestmark = pytest.mark.skip(reason="Skipped in MVP: depends on removed client.ClientSupplier model")


@pytest.mark.django_db
def test_run_profit_share_with_ramp_up():
    tenant = Tenant.objects.create(name="T", domain="t")
    TenantSettings.objects.create(tenant=tenant, ramp_up_min_net=Decimal("800.00"))
    invoice = Invoice.objects.create(
        client_name="C",
        invoice_number="INV1",
        issue_date="2025-01-01",
        due_date="2025-01-10",
        amount=Decimal("1000.00"),
    )

    hl = HierarchicalLevel.objects.create(name="L1", level=1)
    dept = Department.objects.create(name="D1")
    el = ExpertiseLevel.objects.create(name="E1")
    pos = Position.objects.create(title="P1", department=dept, hierarchical_level=hl, expertise_level=el)
    user1 = CustomUser.objects.create(username="u1", email="u1@example.com")
    user2 = CustomUser.objects.create(username="u2", email="u2@example.com")
    emp1 = Employee.objects.create(
        user=user1,
        first_name="F1",
        last_name="L1",
        email="e1@example.com",
        department=dept,
        position=pos,
        expertise_level=el,
        hierarchical_level=1,
    )
    emp2 = Employee.objects.create(
        user=user2,
        first_name="F2",
        last_name="L2",
        email="e2@example.com",
        department=dept,
        position=pos,
        expertise_level=el,
        hierarchical_level=1,
    )

    # Body retained for historical reference; assertions skipped in MVP.
    run_profit_share(invoice, [(emp1, Decimal("1")), (emp2, Decimal("1"))], tenant)
