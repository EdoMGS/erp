from django.template.loader import render_to_string
from weasyprint import HTML

from common import blobstore


def render_invoice_pdf(invoice, qr: str) -> bytes:
    """Render minimal invoice PDF embedding QR payload and store it immutably."""

    html = render_to_string("prodaja/pdf/invoice.html", {"invoice": invoice, "qr": qr})
    pdf_bytes = HTML(string=html).write_pdf()
    if hasattr(invoice, "tenant") and getattr(invoice, "id", None):
        key = f"invoice:{invoice.id}:{getattr(invoice, 'version', 1)}"
        blobstore.put_immutable(
            tenant=invoice.tenant,
            kind="invoice_pdf",
            key=key,
            data=pdf_bytes,
            mimetype="application/pdf",
        )
    return pdf_bytes
