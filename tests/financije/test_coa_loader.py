import pytest

from financije.account_map_hr import ACCOUNT_RULES
from financije.models import Account
from financije.services import load_coa_hr_2025, load_coa_hr_min
from tenants.models import Tenant


@pytest.mark.django_db
def test_load_coa_hr_min_idempotent():
    tenant = Tenant.objects.create(name="T")
    load_coa_hr_min(tenant)
    count1 = Account.objects.filter(tenant=tenant).count()
    load_coa_hr_min(tenant)
    count2 = Account.objects.filter(tenant=tenant).count()
    assert count1 == count2


@pytest.mark.django_db
def test_load_coa_hr_2025_idempotent():
    tenant = Tenant.objects.create(name="T")
    load_coa_hr_2025(tenant)
    count1 = Account.objects.filter(tenant=tenant).count()
    load_coa_hr_2025(tenant)
    count2 = Account.objects.filter(tenant=tenant).count()
    assert count1 == count2
    assert Account.objects.filter(tenant=tenant, number="1400").exists()
    assert Account.objects.filter(tenant=tenant, number="4700").exists()


def test_account_map_covers_expected_events():
    expected = {
        "SALE_INVOICE_POSTED",
        "ADVANCE_RECEIPT",
        "ADVANCE_SETTLEMENT",
        "PURCHASE_INVOICE_POSTED",
        "BANK_CUSTOMER_PAYMENT",
        "BANK_SUPPLIER_PAYMENT",
        "RC_CONSTRUCTION",
        "IC_ACQUISITION",
        "SALE_EXPORT",
        "PROFIT_SHARE",
    }
    assert expected == set(ACCOUNT_RULES)
