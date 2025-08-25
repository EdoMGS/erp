import hashlib
import json
from typing import Any

from django.template.loader import render_to_string
from weasyprint import HTML

from prodaja.models.quote import EstimSnapshot, Quote, QuoteOption


def _get_snapshot(quote: Quote, option: QuoteOption) -> EstimSnapshot | None:
    return EstimSnapshot.objects.filter(quote=quote, option=option).order_by("-created_at").first()


def compute_snapshot_sha256(snapshot: EstimSnapshot) -> str:
    payload = {
        "rounding_policy": snapshot.rounding_policy,
        "norms_version": snapshot.norms_version,
        "price_list_version": snapshot.price_list_version,
        "breakdown": snapshot.breakdown,
    }
    serialized = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(serialized.encode()).hexdigest()


def render_pdf(quote_id: int, option_name: str, variant: str) -> bytes:
    if variant not in {"client", "internal"}:
        raise ValueError("Unknown variant")

    quote = Quote.objects.get(id=quote_id)
    option = quote.options.get(name=option_name)
    snapshot = _get_snapshot(quote, option)
    if not snapshot:
        raise ValueError("Snapshot not found")

    snapshot_sha256 = compute_snapshot_sha256(snapshot)
    context: dict[str, Any] = {
        "quote": quote,
        "option": option,
        "breakdown": snapshot.breakdown,
        "snapshot_sha256": snapshot_sha256,
    }
    template = f"prodaja/pdf/{variant}.html"
    html = render_to_string(template, context)
    return HTML(string=html).write_pdf()


def render_client_pdf(quote_id: int, option_name: str) -> bytes:
    return render_pdf(quote_id, option_name, "client")


def render_internal_pdf(quote_id: int, option_name: str) -> bytes:
    return render_pdf(quote_id, option_name, "internal")
