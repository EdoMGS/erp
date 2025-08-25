import hashlib
import hmac
import json

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from tenants.models import Tenant, TenantUser


@pytest.mark.django_db
def test_acceptance_with_rotated_secondary_secret(settings):
    # Configure rotation: primary=a1, secondary=a0
    settings.ACCEPT_HMAC_SECRETS = ["a1", "a0"]
    t1 = Tenant.objects.create(name="t1", domain="t1")
    user = get_user_model().objects.create_user("u1", password="pw")
    TenantUser.objects.create(tenant=t1, user=user, role="manager")
    client = APIClient()
    client.force_authenticate(user=user)
    quote_body = {
        "tenant": "t1",
        "number": "Q-rot",
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
    create_resp = client.post("/api/quotes", quote_body, format="json", HTTP_X_TENANT="t1")
    assert create_resp.status_code == 201
    quote_id = create_resp.data["id"]

    snap = client.get(f"/api/quotes/{quote_id}", HTTP_X_TENANT="t1").data["snapshot"]
    payload = json.dumps(snap, sort_keys=True)

    # Simulate client still using old secret a0
    old_sig = hmac.new(b"a0", payload.encode(), hashlib.sha256).hexdigest()
    accept1 = client.post(
        f"/api/quotes/{quote_id}/accept",
        {"acceptance_hash": old_sig},
        format="json",
        HTTP_X_TENANT="t1",
        HTTP_IDEMPOTENCY_KEY="k1",
    )
    assert accept1.status_code == 200

    # Idempotent replay
    accept2 = client.post(
        f"/api/quotes/{quote_id}/accept",
        {"acceptance_hash": old_sig},
        format="json",
        HTTP_X_TENANT="t1",
        HTTP_IDEMPOTENCY_KEY="k1",
    )
    assert accept2.status_code == 200
    assert accept2.json() == accept1.json()


@pytest.mark.django_db
def test_acceptance_with_primary_secret(settings):
    # Only primary provided
    settings.ACCEPT_HMAC_SECRETS = ["primary-only"]
    t1 = Tenant.objects.create(name="t1", domain="t1")
    user = get_user_model().objects.create_user("u1", password="pw")
    TenantUser.objects.create(tenant=t1, user=user, role="manager")
    client = APIClient()
    client.force_authenticate(user=user)
    quote_body = {
        "tenant": "t1",
        "number": "Q-prim",
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
    qid = client.post("/api/quotes", quote_body, format="json", HTTP_X_TENANT="t1").data["id"]
    snap = client.get(f"/api/quotes/{qid}", HTTP_X_TENANT="t1").data["snapshot"]
    payload = json.dumps(snap, sort_keys=True)
    sig = hmac.new(b"primary-only", payload.encode(), hashlib.sha256).hexdigest()
    res = client.post(
        f"/api/quotes/{qid}/accept",
        {"acceptance_hash": sig},
        format="json",
        HTTP_X_TENANT="t1",
        HTTP_IDEMPOTENCY_KEY="k2",
    )
    assert res.status_code == 200


@pytest.mark.django_db
def test_acceptance_invalid_signature_returns_400(settings):
    settings.ACCEPT_HMAC_SECRETS = ["a1", "a0"]
    t1 = Tenant.objects.create(name="t1", domain="t1")
    user = get_user_model().objects.create_user("u1", password="pw")
    TenantUser.objects.create(tenant=t1, user=user, role="manager")
    client = APIClient()
    client.force_authenticate(user=user)
    quote_body = {
        "tenant": "t1",
        "number": "Q-bad",
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
    qid = client.post("/api/quotes", quote_body, format="json", HTTP_X_TENANT="t1").data["id"]
    snap = client.get(f"/api/quotes/{qid}", HTTP_X_TENANT="t1").data["snapshot"]
    payload = json.dumps(snap, sort_keys=True)
    bad_sig = hmac.new(b"wrong", payload.encode(), hashlib.sha256).hexdigest()
    res = client.post(
        f"/api/quotes/{qid}/accept",
        {"acceptance_hash": bad_sig},
        format="json",
        HTTP_X_TENANT="t1",
        HTTP_IDEMPOTENCY_KEY="k3",
    )
    assert res.status_code == 400
