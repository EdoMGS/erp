from decimal import Decimal

from prodaja.models import Invoice


def generate_vat_report():
    """Generate simplified VAT report list of dicts."""
    invoices = Invoice.objects.all()
    pdv_report = []
    for invoice in invoices:
        rate = Decimal("0")
        if invoice.total_base:
            rate = (invoice.total_tax / invoice.total_base * Decimal("100")).quantize(Decimal("0.01"))
        pdv_report.append(
            {
                "invoice_number": invoice.number,
                "amount": invoice.total_amount,
                "pdv_rate": rate,
                "pdv_amount": invoice.total_tax,
                "client": invoice.client_name,
            }
        )
    return pdv_report


# NOTE: MVP scope: minimal reporting only.
