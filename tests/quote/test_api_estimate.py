import pytest
from rest_framework.test import APIClient

from tenants.models import Tenant


@pytest.mark.django_db
def test_estimate_endpoint_idempotent():
    Tenant.objects.create(name="t1", domain="t1")
    client = APIClient()
    data = {
        "tenant": "t1",
        "currency": "EUR",
        "vat_rate": "0.25",
        "is_vat_registered": True,
        "risk_band": "Y",
        "contingency_pct": "5",
        "margin_target_pct": "10",
        "items": [
            {
                "type": "fabrication",
                "uom_base": "m2",
                "qty_base": 10.0,
                "area_m2": 10.0,
                "weight_kg": 20.0,
                "conditions": {"mode": "booth"},
            }
        ],
        "options": ["Good", "Better", "Best"],
    }
    key = "abc123"
    resp1 = client.post(
        "/api/quotes/estimate",
        data,
        format="json",
        HTTP_X_TENANT="t1",
        HTTP_IDEMPOTENCY_KEY=key,
    )
    assert resp1.status_code == 200
    assert set(resp1.data["options"].keys()) == {"Good", "Better", "Best"}

    resp2 = client.post(
        "/api/quotes/estimate",
        data,
        format="json",
        HTTP_X_TENANT="t1",
        HTTP_IDEMPOTENCY_KEY=key,
    )
    assert resp2.status_code == 200
    assert resp2.json() == resp1.json()
