from decimal import Decimal

import pytest

from financije.account_map_hr import ACCOUNT_RULES


@pytest.mark.parametrize(
    "event,payload",
    [
        ("SALE_INVOICE_POSTED", {"net": "100", "vat": "25"}),
        ("ADVANCE_RECEIPT", {"amount": "100"}),
        ("ADVANCE_SETTLEMENT", {"amount": "100"}),
        ("PURCHASE_INVOICE_POSTED", {"net": "100", "vat": "25"}),
        ("BANK_CUSTOMER_PAYMENT", {"amount": "100"}),
        ("BANK_SUPPLIER_PAYMENT", {"amount": "100"}),
        ("RC_CONSTRUCTION", {"net": "100", "vat": "25"}),
        ("IC_ACQUISITION", {"net": "100", "vat": "25"}),
        ("SALE_EXPORT", {"net": "100"}),
        (
            "PROFIT_SHARE",
            {"base": "100", "company": "40", "workers": "40", "owner": "20"},
        ),
    ],
)
def test_mapping_balanced(event, payload):
    lines = ACCOUNT_RULES[event](None, payload)
    total_debit = sum(line.get("debit", Decimal("0")) for line in lines)
    total_credit = sum(line.get("credit", Decimal("0")) for line in lines)
    assert total_debit == total_credit
