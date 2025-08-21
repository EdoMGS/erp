import pytest

from prodaja.models.quote import EstimSnapshot, Quote, QuoteOption
from prodaja.services.quote_pdf import compute_snapshot_hash, render_client_pdf
from tenants.models import Tenant


@pytest.mark.django_db
def test_pdf_render_and_hash_changes():
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

    pdf = render_client_pdf(quote.id, option.name)
    assert len(pdf) > 0

    hash1 = compute_snapshot_hash(snapshot)
    snapshot.rounding_policy = "total"
    snapshot.save()
    hash2 = compute_snapshot_hash(snapshot)
    assert hash1 != hash2
