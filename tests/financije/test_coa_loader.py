import pytest

from financije.account_map import ACCOUNT_RULES
from financije.models import Account
from financije.services import load_coa_hr_min
from tenants.models import Tenant


@pytest.mark.django_db
def test_load_coa_hr_min_idempotent():
    tenant = Tenant.objects.create(name="T")
    load_coa_hr_min(tenant)
    count1 = Account.objects.filter(tenant=tenant).count()
    load_coa_hr_min(tenant)
    count2 = Account.objects.filter(tenant=tenant).count()
    assert count1 == count2


def test_account_map_covers_expected_events():
    expected = {
        "SALE_INVOICE_POSTED",
        "PURCHASE_INVOICE_POSTED",
        "ADVANCE_RECEIPT",
        "ADVANCE_SETTLEMENT",
        "BANK_CUSTOMER_PAYMENT",
        "BANK_SUPPLIER_PAYMENT",
        "PROFIT_SHARE",
    }
    assert expected == set(ACCOUNT_RULES)
