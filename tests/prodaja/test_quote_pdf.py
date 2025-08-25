import pytest

from prodaja.models.quote import EstimSnapshot, Quote, QuoteOption
from prodaja.pdf.render import (
    compute_snapshot_sha256,
    render_client_pdf,
    render_internal_pdf,
)
from tenants.models import Tenant


def _create_data():
    tenant = Tenant.objects.create(name="t1", domain="t1")
    quote = Quote.objects.create(
        tenant=tenant,
        number="Q1",
        currency="EUR",
        vat_rate="0.25",
        is_vat_registered=True,
        customer_name="ACME",
        risk_band="Y",
        contingency_pct="5",
        margin_target_pct="10",
    )
    option = QuoteOption.objects.create(tenant=tenant, quote=quote, name="Good")
    snapshot = EstimSnapshot.objects.create(
        tenant=tenant,
        quote=quote,
        option=option,
        norms_version="v1",
        price_list_version="p1",
        rounding_policy="item",
        input_data={},
        breakdown={
            "components": {"material": 100},
            "net_total": 100,
            "vat_total": 25,
            "gross_total": 125,
        },
        version="1",
    )
    return quote, option, snapshot


@pytest.mark.django_db
def test_client_and_internal_pdfs_generated():
    quote, option, _ = _create_data()
    client_pdf = render_client_pdf(quote.id, option.name)
    internal_pdf = render_internal_pdf(quote.id, option.name)
    assert len(client_pdf) > 0
    assert len(internal_pdf) > 0


@pytest.mark.django_db
def test_snapshot_hash_changes_on_rounding_policy_change():
    _, option, snapshot = _create_data()
    hash1 = compute_snapshot_sha256(snapshot)
    snapshot.rounding_policy = "total"
    snapshot.save()
    hash2 = compute_snapshot_sha256(snapshot)
    assert hash1 != hash2
