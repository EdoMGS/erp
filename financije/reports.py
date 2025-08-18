from financije.models import Invoice


def generate_vat_report():
    """Generate simplified VAT report list of dicts."""
    invoices = Invoice.objects.all()
    pdv_report = []
    for invoice in invoices:
        pdv_report.append(
            {
                "invoice_number": invoice.invoice_number,
                "amount": invoice.amount,
                "pdv_rate": invoice.pdv_rate,
                "pdv_amount": invoice.pdv_amount,
                "client": invoice.client_name,
            }
        )
    return pdv_report


# NOTE: MVP scope: minimal reporting only.
