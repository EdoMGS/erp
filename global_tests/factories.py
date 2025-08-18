"""Central lightweight test factories (manual, no factory-boy dependency yet)."""
from __future__ import annotations

from uuid import uuid4
from decimal import Decimal
from django.contrib.auth import get_user_model


def create_financial_details():
    from financije.models import FinancialDetails
    return FinancialDetails.objects.create()


def create_project():  # removed legacy dependency
    raise NotImplementedError("Projekt model (production domain) removed in MVP scope")


def create_production():  # removed legacy dependency
    raise NotImplementedError("Proizvodnja model removed in MVP scope")


def create_employee(username_prefix: str = "emp"):
    from ljudski_resursi.models import Employee
    User = get_user_model()
    user = User.objects.create(username=f"{username_prefix}-{uuid4().hex[:8]}")
    return Employee.objects.create(user=user)


def create_work_order():  # removed legacy dependency
    raise NotImplementedError("RadniNalog removed in MVP scope")


def create_artikl_chain():  # removed legacy dependency
    raise NotImplementedError("Inventory chain removed in MVP scope")


def create_material(*_args, **_kwargs):  # removed legacy dependency
    raise NotImplementedError("Materijal removed in MVP scope")
