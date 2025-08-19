import pytest
from prodaja.models import Invoice
from tenants.models import Tenant


@pytest.mark.django_db
def test_invoice_minimal_create():
    tenant = Tenant.objects.create(name="T")
    inv = Invoice.objects.create(tenant=tenant, client_name="X", issue_date="2025-01-01")
    assert inv.pk is not None
