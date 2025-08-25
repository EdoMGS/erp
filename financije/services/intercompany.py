"""Intercompany utilities."""

from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from client_app.models import ClientSupplier
from financije.models.invoice import Invoice, InvoiceLine
from tenants.models import Tenant


@transaction.atomic
def create_interco_invoice(
    sender: Tenant,
    receiver: Tenant,
    asset,
    amount: Decimal,
    vat_rate: Decimal,
    *,
    sender_in_vat: bool = True,
):
    """Create an intercompany invoice for asset usage.

    The receiver becomes a ``ClientSupplier`` in the sender's tenant. Only a
    minimal subset of fields is populated to satisfy model requirements. This
    helper focuses on invoice creation needed for test coverage; symmetrical
    ledger postings are handled elsewhere.
    """

    today = timezone.now().date()

    client, _ = ClientSupplier.objects.get_or_create(
        name=receiver.name,
        defaults={
            "address": "N/A",
            "email": f"{receiver.name.lower()}@example.com",
            "phone": "000",
            "oib": str(receiver.id).zfill(11),
            "city": "",
            "postal_code": "",
        },
    )

    invoice = Invoice.objects.create(
        tenant=sender,
        client=client,
        invoice_number=f"IC-{sender.id}-{receiver.id}-{today.strftime('%Y%m%d')}",
        issue_date=today,
        due_date=today,
        pdv_rate=vat_rate if sender_in_vat else Decimal("0.00"),
    )

    description = str(asset)
    if not sender_in_vat:
        description += " - nije u sustavu PDV-a"

    InvoiceLine.objects.create(
        invoice=invoice,
        description=description,
        quantity=Decimal("1"),
        unit_price=amount,
        tax_rate=vat_rate if sender_in_vat else Decimal("0.00"),
    )

    return invoice


__all__ = ["create_interco_invoice"]
