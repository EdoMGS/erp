import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from prodaja.models.quote import Quote, QuoteRevision
from tenants.models import Tenant, TenantUser


@pytest.mark.django_db
def test_quote_revision_creates_snapshot_and_updates_revision():
    tenant = Tenant.objects.create(name="t1", domain="t1")
    user = get_user_model().objects.create_user("u1", password="pw")
    TenantUser.objects.create(tenant=tenant, user=user, role="manager")
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
    resp = client.post(
        "/api/quotes",
        quote_body,
        format="json",
        HTTP_X_TENANT="t1",
    )
    assert resp.status_code == 201
    quote_id = resp.data["id"]
    detail1 = client.get(f"/api/quotes/{quote_id}", HTTP_X_TENANT="t1").json()
    initial_total = detail1["snapshot"]["breakdown"]["Good"]["net_total"]

    revised_body = quote_body.copy()
    revised_body["items"] = [dict(revised_body["items"][0], qty_base=20.0, area_m2=20.0)]
    rev_resp = client.post(
        f"/api/quotes/{quote_id}/revision",
        {
            "reason_code": "client_change",
            "delta": {"qty_base": [10.0, 20.0]},
            "input": revised_body,
        },
        format="json",
        HTTP_X_TENANT="t1",
    )
    assert rev_resp.status_code == 200
    assert rev_resp.data["revision"] == 2

    quote = Quote.objects.get(id=quote_id)
    assert quote.revision == 2

    revision = QuoteRevision.objects.get(parent_id=quote_id)
    assert revision.reason_code == "client_change"
    assert revision.prev_snapshot.version == "1"
    assert revision.new_snapshot.version == "2"
    assert revision.delta == {"qty_base": [10.0, 20.0]}

    detail2 = client.get(f"/api/quotes/{quote_id}", HTTP_X_TENANT="t1").json()
    new_total = detail2["snapshot"]["breakdown"]["Good"]["net_total"]
    assert new_total > initial_total
