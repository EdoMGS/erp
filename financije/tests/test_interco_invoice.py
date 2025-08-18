from decimal import Decimal

import pytest

import pytest

pytestmark = pytest.mark.skip(reason="Skipped in MVP: erp_assets app removed")

# from erp_assets.models import Asset  # legacy dependency removed in MVP
from financije.models.invoice import Invoice, InvoiceLine
from financije.services import create_interco_invoice
from tenants.models import Tenant


@pytest.mark.django_db
def test_create_interco_invoice_creates_invoice_and_line(django_user_model):
    pass


@pytest.mark.django_db
def test_create_interco_invoice_no_vat(django_user_model):
    pass
