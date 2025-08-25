from __future__ import annotations

from django.conf import settings

from .gateway import send_invoice
from .pdf import build_pdf
from .ubl import Invoice, InvoiceItem, build_ubl

__all__ = ["Invoice", "InvoiceItem", "process_invoice"]


def process_invoice(invoice: Invoice) -> tuple[str, dict[str, str], bytes]:
    """Generate UBL, submit it via the gateway and produce a PDF snapshot."""
    if not getattr(settings, "FISKALIZACIJA_ERACUN", False):
        raise RuntimeError("FISKALIZACIJA_ERACUN disabled")
    xml = build_ubl(invoice)
    result = send_invoice(xml)
    pdf = build_pdf(xml, result["jir"])
    return xml, result, pdf
