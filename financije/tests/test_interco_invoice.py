from decimal import Decimal

import pytest

from erp_assets.models import Asset
from financije.models.invoice import Invoice, InvoiceLine
from financije.services import create_interco_invoice
from tenants.models import Tenant


@pytest.mark.django_db
def test_create_interco_invoice_creates_invoice_and_line(django_user_model):
    sender = Tenant.objects.create(name="Sender")
    receiver = Tenant.objects.create(name="Receiver")
    asset = Asset.objects.create(
        type="vehicle", value=10000, amort_plan="plan", owner_tenant=sender
    )
    amount = Decimal("1000.00")
    vat_rate = Decimal("25.00")

    invoice = create_interco_invoice(sender, receiver, asset, amount, vat_rate)

    assert Invoice.objects.filter(pk=invoice.pk).exists()
    line = InvoiceLine.objects.get(invoice=invoice)
    assert line.unit_price == amount
    assert line.tax_rate == vat_rate
    assert str(asset) in line.description
    assert invoice.pdv_rate == vat_rate


@pytest.mark.django_db
def test_create_interco_invoice_no_vat(django_user_model):
    sender = Tenant.objects.create(name="Sender")
    receiver = Tenant.objects.create(name="Receiver")
    asset = Asset.objects.create(
        type="vehicle", value=10000, amort_plan="plan", owner_tenant=sender
    )
    amount = Decimal("1000.00")
    vat_rate = Decimal("25.00")

    invoice = create_interco_invoice(sender, receiver, asset, amount, vat_rate, sender_in_vat=False)

    assert Invoice.objects.filter(pk=invoice.pk).exists()
    line = InvoiceLine.objects.get(invoice=invoice)
    assert line.unit_price == amount
    assert line.tax_rate == Decimal("0.00")
    assert "nije u sustavu PDV-a" in line.description
    assert invoice.pdv_rate == Decimal("0.00")
