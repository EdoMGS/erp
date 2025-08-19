from decimal import Decimal
import pytest
from django.utils import timezone
from tenants.models import Tenant
from prodaja.models import Invoice, InvoiceLine, InvoiceSequence  # in unified models file
from prodaja.services.invoice_post import post_invoice
from financije.ledger import trial_balance, JournalEntry


@pytest.fixture()
def tenant():
    return Tenant.objects.create(name="T")


@pytest.mark.django_db
def test_invoice_post_simple(tenant: Tenant):
    inv = Invoice.objects.create(tenant=tenant, client_name="Kupac d.o.o.")
    InvoiceLine.objects.create(invoice=inv, description="Usluga A", qty=Decimal('2'), unit_price=Decimal('100'), tax_rate=Decimal('25'))
    InvoiceLine.objects.create(invoice=inv, description="Usluga B", qty=Decimal('1'), unit_price=Decimal('200'), tax_rate=Decimal('13'))

    post_invoice(inv)

    inv.refresh_from_db()
    assert inv.is_posted
    assert inv.number.startswith("001-")
    # Totals
    assert inv.total_base == Decimal('400.00')
    # tax = 2*100*0.25 + 1*200*0.13 = 50 + 26 = 76
    assert inv.total_tax == Decimal('76.00')
    assert inv.total_amount == Decimal('476.00')

    # GL
    tb = {row[0]: row for row in trial_balance(tenant=tenant, show_netted=False)}
    # row => (account, debit, credit, balance); balance = debit - credit
    assert tb['120'][1] - tb['120'][2] == Decimal('476.00')  # AR debit net
    assert tb['400'][1] - tb['400'][2] == Decimal('-400.00')  # Revenue credit
    assert tb['2680'][1] - tb['2680'][2] == Decimal('-76.00')  # VAT payable


@pytest.mark.django_db
def test_invoice_sequence_increment(tenant: Tenant):
    inv1 = Invoice.objects.create(tenant=tenant, client_name="A")
    InvoiceLine.objects.create(invoice=inv1, description="L1", qty=1, unit_price=Decimal('10'), tax_rate=Decimal('25'))
    post_invoice(inv1)

    inv2 = Invoice.objects.create(tenant=tenant, client_name="B")
    InvoiceLine.objects.create(invoice=inv2, description="L2", qty=1, unit_price=Decimal('10'), tax_rate=Decimal('25'))
    post_invoice(inv2)

    assert inv1.number != inv2.number


@pytest.mark.django_db
def test_ira_export(tenant: Tenant):
    inv = Invoice.objects.create(tenant=tenant, client_name="Kupac")
    InvoiceLine.objects.create(invoice=inv, description="U1", qty=2, unit_price=Decimal('100'), tax_rate=Decimal('25'))
    InvoiceLine.objects.create(invoice=inv, description="U2", qty=1, unit_price=Decimal('200'), tax_rate=Decimal('13'))
    post_invoice(inv)

    from reports.ira_export import export_ira_csv
    csv_data = export_ira_csv()
    assert "001-" in csv_data
    assert ";Kupac;" in csv_data or ";Kupac d.o.o.;" in csv_data
    assert "400.00;76.00;476.00" in csv_data
