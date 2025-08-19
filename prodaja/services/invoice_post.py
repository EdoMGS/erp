from __future__ import annotations
from decimal import Decimal
from django.db import transaction
from prodaja import models as prod_models
Invoice = prod_models.Invoice
from financije.ledger import post_entry
from financije.models import Account


@transaction.atomic
def post_invoice(inv: Invoice):
    if inv.is_posted:
        return inv
    # Ensure required accounts exist (test safety / minimal seed)
    for num, name, atype in [
        ("120", "Kupci", "active"),
        ("400", "Prihodi usluge", "income"),
        ("2680", "PDV izlazni", "passive"),
    ]:
        Account.objects.get_or_create(number=num, defaults={"name": name, "account_type": atype})
    # Recompute totals (lines already saved) prior to numbering
    inv.recompute_totals()
    inv.status = "posted"
    inv.assign_number()
    # group lines by tax rate for multi-rate VAT
    base_total = inv.total_base
    tax_total = inv.total_tax
    # Post GL: DR 120 (AR) / CR 400 (Revenue) / CR 2680 (VAT payable)
    lines = []
    if base_total:
        lines.append({"account": "400", "dc": "C", "amount": base_total})
    if tax_total:
        lines.append({"account": "2680", "dc": "C", "amount": tax_total})
    if base_total or tax_total:
        lines.append({"account": "120", "dc": "D", "amount": base_total + tax_total})
    post_entry(
        tenant=inv.tenant,
        ref=f"INV-{inv.number}",
        kind="invoice_post",
        memo=f"Invoice {inv.number} customer {inv.client_name}",
        lines=lines,
    )
    inv.save(update_fields=["number", "status", "total_base", "total_tax", "total_amount", "updated_at"])
    return inv
