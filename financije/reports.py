from financije.models import Invoice

def generate_vat_report():
    # Logika za generiranje izvještaja o PDV-u
    invoices = Invoice.objects.all()
    pdv_report = []
    for invoice in invoices:
        pdv_report.append({
            'invoice_number': invoice.invoice_number,
            'amount': invoice.amount,
            'pdv_rate': invoice.pdv_rate,
            'pdv_amount': invoice.pdv_amount,
            'client': invoice.client.name
        })
    return pdv_report

# Provjerite da li svi modeli i polja koje koristite postoje u models.py
