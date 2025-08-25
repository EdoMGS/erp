from django.template.loader import render_to_string

try:
    from weasyprint import HTML
except Exception:  # pragma: no cover - fallback if system dependencies missing
    HTML = None


def render_profit_share_pdf(*, base, company, workers, owner, rounding_diff) -> bytes:
    """Render a minimal profit share PDF."""
    html = render_to_string(
        "project_costing/pdf/profit_share.html",
        {
            "base": base,
            "company": company,
            "workers": workers,
            "owner": owner,
            "rounding_diff": rounding_diff,
        },
    )
    if HTML is None:
        return html.encode()
    return HTML(string=html).write_pdf()
