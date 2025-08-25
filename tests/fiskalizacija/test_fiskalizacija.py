from datetime import date
from decimal import Decimal

import pytest
from django.conf import settings

from fiskalizacija import Invoice, InvoiceItem, process_invoice


def test_demo_invoice_flow():
    settings.FISKALIZACIJA_ERACUN = True
    invoice = Invoice(
        number="INV-001",
        issue_date=date(2025, 1, 1),
        seller_oib="12345678901",
        buyer_oib="10987654321",
        items=[InvoiceItem("Widget", Decimal("1"), Decimal("100"), Decimal("0.25"))],
    )
    xml, result, pdf = process_invoice(invoice)
    assert "Invoice" in xml
    assert result["jir"] and result["zki"]
    assert pdf.startswith(b"%PDF")
    assert result["jir"].encode() in pdf
    assert b"QR:" in pdf and b"HASH:" in pdf


def test_feature_flag_required():
    settings.FISKALIZACIJA_ERACUN = False
    invoice = Invoice(
        number="INV-002",
        issue_date=date(2025, 1, 2),
        seller_oib="12345678901",
        buyer_oib="10987654321",
        items=[InvoiceItem("Widget", Decimal("1"), Decimal("100"), Decimal("0.25"))],
    )
    with pytest.raises(RuntimeError):
        process_invoice(invoice)
