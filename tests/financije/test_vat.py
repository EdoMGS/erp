from decimal import Decimal

from financije.vat import VatBookEntry, VatCode, VatType, aggregate_pdv_o


def test_pdv_o_aggregation_balance():
    standard = VatCode(Decimal("0.25"), VatType.STANDARD)
    reduced = VatCode(Decimal("0.13"), VatType.REDUCED_13)
    rc = VatCode(Decimal("0.25"), VatType.REVERSE_CHARGE)
    ic = VatCode(Decimal("0.25"), VatType.IC_ACQ)
    export = VatCode(Decimal("0.00"), VatType.EXPORT)

    sales = [
        VatBookEntry("sale", standard, Decimal("100")),
        VatBookEntry("sale", reduced, Decimal("100")),
        VatBookEntry("sale", export, Decimal("100")),
    ]
    purchases = [
        VatBookEntry("purchase", rc, Decimal("100")),
        VatBookEntry("purchase", ic, Decimal("100")),
    ]

    totals = aggregate_pdv_o(sales, purchases)

    assert totals["sales"]["25"] == {"base": Decimal("100.00"), "vat": Decimal("25.00")}
    assert totals["sales"]["13"] == {"base": Decimal("100.00"), "vat": Decimal("13.00")}
    assert totals["sales"]["export"] == {"base": Decimal("100.00"), "vat": Decimal("0.00")}
    assert totals["sales"]["rc"] == {"base": Decimal("100.00"), "vat": Decimal("25.00")}
    assert totals["sales"]["ic_acq"] == {"base": Decimal("100.00"), "vat": Decimal("25.00")}
    assert totals["purchases"]["rc"] == {"base": Decimal("100.00"), "vat": Decimal("25.00")}
    assert totals["purchases"]["ic_acq"] == {"base": Decimal("100.00"), "vat": Decimal("25.00")}

    # IRA/URA sums equal PDV-O totals
    ira_base = sum(e.base for e in sales) + sum(
        e.base for e in purchases if e.vat_code.type in {VatType.REVERSE_CHARGE, VatType.IC_ACQ}
    )
    ura_base = sum(e.base for e in purchases)

    assert ira_base == sum(bucket["base"] for bucket in totals["sales"].values())
    assert ura_base == sum(bucket["base"] for bucket in totals["purchases"].values())
