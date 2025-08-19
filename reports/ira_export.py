from __future__ import annotations

import csv
from decimal import Decimal
from io import StringIO

from prodaja.models import Invoice


def export_ira_csv(queryset=None) -> str:
    """Generate IRA (Izdani Racuni) CSV with sums by tax rate and invoice details.
    Columns: number, date, client, base_total, tax_total, gross_total, tax_breakdown(json)
    """
    qs = queryset or Invoice.objects.filter(status="posted").select_related("tenant")
    out = StringIO()
    writer = csv.writer(out, delimiter=';')
    writer.writerow(["Broj", "Datum", "Klijent", "Osnovica", "PDV", "Ukupno", "PDV_po_stopama"])
    for inv in qs.order_by('issue_date', 'id'):
        # breakdown by tax rate
        breakdown = {}
        for line in inv.lines.all():
            r = str(line.tax_rate)
            breakdown.setdefault(r, {"base": Decimal('0'), "tax": Decimal('0')})
            breakdown[r]["base"] += line.base_amount
            breakdown[r]["tax"] += line.tax_amount
        # serialize breakdown as rate1:base|tax,rate2:base|tax
        parts = []
        for rate, sums in sorted(breakdown.items(), key=lambda x: Decimal(x[0])):
            parts.append(f"{rate}:{sums['base']:.2f}|{sums['tax']:.2f}")
        writer.writerow(
            [
                inv.number,
                inv.issue_date.isoformat(),
                inv.client_name,
                f"{inv.total_base:.2f}",
                f"{inv.total_tax:.2f}",
                f"{inv.total_amount:.2f}",
                ",".join(parts),
            ]
        )
    return out.getvalue()
