from django.template.loader import render_to_string
from weasyprint import HTML


def render_invoice_pdf(invoice, qr: str) -> bytes:
    """Render minimal invoice PDF embedding QR payload."""

    html = render_to_string("prodaja/pdf/invoice.html", {"invoice": invoice, "qr": qr})
    return HTML(string=html).write_pdf()
