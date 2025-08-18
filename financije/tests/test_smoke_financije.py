import pytest
from financije.models.invoice import Invoice


@pytest.mark.django_db
def test_invoice_minimal_create():
    inv = Invoice.objects.create(
        client_name="X",
        invoice_number="INVTEST",
        issue_date="2025-01-01",
        due_date="2025-01-02",
        amount=0,
    )
    assert inv.pk is not None
