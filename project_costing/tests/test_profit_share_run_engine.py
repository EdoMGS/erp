import pytest
from decimal import Decimal
from tenants.models import Tenant, TenantSettings
from financije.models.invoice import Invoice
from client.models import ClientSupplier
from ljudski_resursi.models import (
    Employee,
    Position,
    Department,
    HierarchicalLevel,
    ExpertiseLevel,
)
from accounts.models import CustomUser
from project_costing.profit_share import run_profit_share


@pytest.mark.django_db
def test_run_profit_share_with_ramp_up():
    tenant = Tenant.objects.create(name="T", domain="t")
    TenantSettings.objects.create(tenant=tenant, ramp_up_min_net=Decimal("800.00"))
    client = ClientSupplier.objects.create(
        name="C",
        address="A",
        email="c@example.com",
        phone="1",
        oib="12345678901",
        city="Z",
        postal_code="10000",
    )
    invoice = Invoice.objects.create(
        client=client,
        invoice_number="INV1",
        issue_date="2025-01-01",
        due_date="2025-01-10",
        amount=Decimal("1000.00"),
    )

    hl = HierarchicalLevel.objects.create(name="L1", level=1)
    dept = Department.objects.create(name="D1")
    el = ExpertiseLevel.objects.create(name="E1")
    pos = Position.objects.create(
        title="P1", department=dept, hierarchical_level=hl, expertise_level=el
    )
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

    run = run_profit_share(invoice, [(emp1, Decimal("1")), (emp2, Decimal("1"))], tenant)
    participants = list(run.participants.order_by("employee_id"))
    assert run.pool_30 == Decimal("300.00")
    assert participants[0].final_amount == Decimal("800.00")
    assert participants[0].ramp_up_adjustment == Decimal("650.00")
    assert participants[1].final_amount == Decimal("800.00")

