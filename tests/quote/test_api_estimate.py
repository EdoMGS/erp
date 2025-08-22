import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from tenants.models import Tenant, TenantUser


@pytest.mark.django_db
def test_estimate_endpoint_idempotent():
    tenant = Tenant.objects.create(name="t1", domain="t1")
    user = get_user_model().objects.create_user("u1", password="pw")
    TenantUser.objects.create(tenant=tenant, user=user, role="staff")
    client = APIClient()
    client.force_authenticate(user=user)
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


@pytest.mark.django_db
def test_estimate_rate_limit():
    tenant = Tenant.objects.create(name="t1", domain="t1")
    user = get_user_model().objects.create_user("u1", password="pw")
    TenantUser.objects.create(tenant=tenant, user=user, role="staff")
    client = APIClient()
    client.force_authenticate(user=user)
    from django.core.cache import cache

    cache.clear()
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
                "qty_base": 1.0,
                "area_m2": 1.0,
                "weight_kg": 2.0,
                "conditions": {"mode": "booth"},
            }
        ],
        "options": ["Good"],
    }
    for i in range(30):
        resp = client.post(
            "/api/quotes/estimate",
            data,
            format="json",
            HTTP_X_TENANT="t1",
            HTTP_IDEMPOTENCY_KEY=str(i),
        )
        assert resp.status_code == 200
    resp = client.post(
        "/api/quotes/estimate",
        data,
        format="json",
        HTTP_X_TENANT="t1",
        HTTP_IDEMPOTENCY_KEY="overflow",
    )
    assert resp.status_code == 429
