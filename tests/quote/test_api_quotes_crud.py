import hashlib
import hmac
import json

import pytest
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from tenants.models import Tenant, TenantUser


@pytest.mark.django_db
def test_quote_crud_and_acceptance():
    t1 = Tenant.objects.create(name="t1", domain="t1")
    Tenant.objects.create(name="t2", domain="t2")
    user = get_user_model().objects.create_user("u1", password="pw")
    TenantUser.objects.create(tenant=t1, user=user, role="manager")
    client = APIClient()
    client.force_authenticate(user=user)
    quote_body = {
        "tenant": "t1",
        "number": "Q-1",
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
    create_resp = client.post(
        "/api/quotes",
        quote_body,
        format="json",
        HTTP_X_TENANT="t1",
    )
    assert create_resp.status_code == 201
    quote_id = create_resp.data["id"]

    # isolation: other tenant can't read
    not_found = client.get(f"/api/quotes/{quote_id}", HTTP_X_TENANT="t2")
    assert not_found.status_code == 403

    get_resp = client.get(f"/api/quotes/{quote_id}", HTTP_X_TENANT="t1")
    assert get_resp.status_code == 200
    snapshot = get_resp.data["snapshot"]

    send_resp = client.post(f"/api/quotes/{quote_id}/send", {}, HTTP_X_TENANT="t1")
    assert send_resp.status_code == 200
    assert send_resp.data["status"] == "sent"

    payload = json.dumps(snapshot, sort_keys=True)
    expected_hash = hmac.new(
        settings.SECRET_KEY.encode(), payload.encode(), hashlib.sha256
    ).hexdigest()
    key = "accept1"
    accept_resp = client.post(
        f"/api/quotes/{quote_id}/accept",
        {"acceptance_hash": expected_hash},
        format="json",
        HTTP_X_TENANT="t1",
        HTTP_IDEMPOTENCY_KEY=key,
    )
    assert accept_resp.status_code == 200
    assert accept_resp.data["status"] == "accepted"
    assert accept_resp.data["accepted_at"] is not None

    # idempotent
    accept_resp2 = client.post(
        f"/api/quotes/{quote_id}/accept",
        {"acceptance_hash": expected_hash},
        format="json",
        HTTP_X_TENANT="t1",
        HTTP_IDEMPOTENCY_KEY=key,
    )
    assert accept_resp2.status_code == 200
    assert accept_resp2.json() == accept_resp.json()
