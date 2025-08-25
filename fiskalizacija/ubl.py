from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from xml.etree.ElementTree import Element, SubElement, tostring

from common import blobstore


@dataclass
class InvoiceItem:
    description: str
    quantity: Decimal
    unit_price: Decimal
    vat_rate: Decimal


@dataclass
class Invoice:
    number: str
    issue_date: date
    seller_oib: str
    buyer_oib: str
    items: list[InvoiceItem]


def build_ubl(invoice: Invoice) -> str:
    """Render a minimal UBL 2.1 XML representation for the given invoice."""
    ns_inv = "{urn:oasis:names:specification:ubl:schema:xsd:Invoice-2}"
    ns_cbc = "{urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2}"
    ns_cac = "{urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2}"
    root = Element(f"{ns_inv}Invoice")
    SubElement(root, f"{ns_cbc}ID").text = invoice.number
    SubElement(root, f"{ns_cbc}IssueDate").text = invoice.issue_date.isoformat()
    supplier = SubElement(root, f"{ns_cac}AccountingSupplierParty")
    SubElement(supplier, f"{ns_cbc}CompanyID").text = invoice.seller_oib
    customer = SubElement(root, f"{ns_cac}AccountingCustomerParty")
    SubElement(customer, f"{ns_cbc}CompanyID").text = invoice.buyer_oib
    total = Decimal("0")
    for item in invoice.items:
        line = SubElement(root, f"{ns_cac}InvoiceLine")
        SubElement(line, f"{ns_cbc}ID").text = item.description
        SubElement(line, f"{ns_cbc}InvoicedQuantity").text = f"{item.quantity}"
        line_total = item.quantity * item.unit_price
        SubElement(line, f"{ns_cbc}LineExtensionAmount").text = f"{line_total:.2f}"
        total += line_total * (Decimal("1") + item.vat_rate)
    monetary = SubElement(root, f"{ns_cac}LegalMonetaryTotal")
    SubElement(monetary, f"{ns_cbc}PayableAmount").text = f"{total:.2f}"
    xml = tostring(root, encoding="unicode")
    if hasattr(invoice, "tenant") and getattr(invoice, "id", None):
        key = f"invoice:{invoice.id}:{getattr(invoice, 'version', 1)}"
        blobstore.put_immutable(
            tenant=invoice.tenant,
            kind="invoice_ubl",
            key=key,
            data=xml.encode(),
            mimetype="application/xml",
        )
    return xml
