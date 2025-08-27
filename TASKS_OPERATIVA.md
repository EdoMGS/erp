# TASKS_OPERATIVA.md — Sales, Work Orders & Operations

## Vizija

ERP mora pokriti puni operativni tok male proizvodno-uslužne firme (bravarija + farbanje): **od ponude do radnog naloga, troškovnika, QC i isplate radnicima**. Sve povezuje u Ledger i Profit‑Share 50‑30‑20.

Cilj: **radnik vidi nalog, trošak i svoj udio**, direktor vidi **P&L i cashflow**, a knjigovođa dobiva čiste izvještaje.

---

## O0 — Prodaja & Ponude (Sales & Quotes)

* [ ] **Modeli** (`prodaja/models/quote.py`): Quote, QuoteItem, QuoteOption, QuoteRevision, EstimSnapshot.
* [ ] **Estimator servis** (`services/estimator/…`): materijal, boja, rad, logistika; G/B/B opcije.
* [ ] **API endpoints** (DRF):

  * POST /api/quotes/estimate (računa G/B/B)
  * POST /api/quotes (kreira draft)
  * POST /api/quotes/{id}/send (mark sent)
  * POST /api/quotes/{id}/accept (status accepted)
  * POST /api/quotes/{id}/revision (change order)
* [ ] **PDF**:

  * Klijent: cijena po opcijama, uvjeti, QR link.
  * Interni: norme, satnica, kalkulacije.
* [ ] **Knjiženje**: Accept → Invoice → fiskalizacija → Ledger.
* [ ] **Testovi**: estimator (property), API CRUD, PDF > 0 kB.

---

## O1 — Radni nalozi (Work Orders)

* [ ] **Modeli** (`proizvodnja/models/work_order.py`): WorkOrder, WorkTask.

  * status (draft/in_progress/done)
  * veze na Quote/Invoice
  * due_date, assigned_to, attachments (fotke)
* [ ] **API endpoints**:

  * POST /api/workorders (create)
  * GET /api/workorders/{id} (details + tasks)
  * POST /api/workorders/{id}/start / complete
* [ ] **JobCosting** (`job_costing/services.py`):

  * materijal (povezati na skladiste)
  * rad (sati × norma × cijena)
  * stroj (skela, dizalica)
* [ ] **QC** (`qc/models.py`): QCPlan, QCCheck (npr. DFT, foto before/after).
* [ ] **Testovi**: kreiranje WO, dodavanje materijala, završetak + QC pass.

---

## O2 — Nabava & Skladište

* [ ] **PurchaseOrder** + ulaz robe.
* [ ] **Skladiste** (`inventory/models.py`): StockItem, StockMove, rezervacije.
* [ ] **Integracija**: WO generira PurchaseReq ako materijal fali.
* [ ] **Testovi**: ulaz robe, izlaz na WO, FEFO za boje.

---

## O3 — Profit‑Share & Payroll

* [ ] **ProfitShareEngine** (`profitshare/services.py`): 50‑30‑20 pool na temelju Invoice.

  * 30% pool → raspodjela po radnicima na WO.
  * Ramp‑up zaštita (min 800 € neto).
* [ ] **PayrollRun** (`hr/payroll.py`): bruto↔neto↔trošak; integracija s profit‑share.
* [ ] **JOPPD export** (XSD validacija).
* [ ] **Testovi**: 3 radnika, različiti scenariji, JOPPD validan.

---

## O4 — UX & Delivery

* [ ] **Micro‑dashboard**: otvoreni nalozi, statusi, pool 50‑30‑20.
* [ ] **PDF/email**: ponuda, faktura, platna lista, QC report.
* [ ] **Runbook**: fiskalizacija replay, PDV‑O export, JOPPD export.
* [ ] **Testovi**: e2e (Quote → WO → Invoice → Ledger → ProfitShare → Payroll).

---

## Definition of Done (v1.0 Operativa)

* Ponuda do fakture → < 5 min, bez ručnog prepisivanja.
* Svaki WO ima troškovnik i QC evidenciju.
* Profit‑share i plaće jasno vidljivi radnicima.
* Svi financijski događaji završavaju u Ledgeru.
* Period lock + audit trail čuvaju integritet.

---

## Napomene

* **Tenancy**: svi modeli imaju `tenant` FK.
* **Money**: Decimal, HALF_UP, 2 dec.
* **Idempotency**: ključ `(tenant, source, version)`.
* **Integracija**: Quote→WO→Invoice→Ledger→ProfitShare→Payroll.
* **CI/CD**: pytest + pre‑commit obavezno green.

```
  # placeholder: mark as sent (email wiring later)
  q: Quote = self.get_object()
  q.status = Quote.Status.SENT
  q.save(update_fields=["status"]) 
  return Response({"status": "sent"})
```

@action(detail=True, methods=["post"], url_path="accept")
def accept(self, request, pk=None):
  q: Quote = self.get_object()
  if q.status not in (Quote.Status.SENT, Quote.Status.DRAFT):
    return Response({"error": "invalid-status"}, status=status.HTTP_409_CONFLICT)
  q.status = Quote.Status.ACCEPTED
  q.save(update_fields=["status"])
  # TODO: convert to WorkOrder + optionally create Invoice draft
  return Response({"status": "accepted"})

@action(detail=True, methods=["post"], url_path="revision")
def revision(self, request, pk=None):
  q: Quote = self.get_object()
  reason = request.data.get("reason", "")
  delta = request.data.get("delta", {})
  QuoteRevision.objects.create(tenant=q.tenant, parent=q, reason=reason, delta_json=delta, user=request.user)
  q.revision += 1
  q.save(update_fields=["revision"])
  return Response({"status": "revised", "revision": q.revision})

# ================================

# FILE: prodaja/pdf/quote.py

# ================================

from __future__ import annotations
from django.template.loader import render_to_string

try:
  from weasyprint import HTML  # preferred
  def _html_to_pdf_bytes(html: str) -> bytes:
    return HTML(string=html).write_pdf()
except Exception:
  def _html_to_pdf_bytes(html: str) -> bytes:  # fallback for tests
    return html.encode("utf-8")

def render_client_pdf(*, quote, breakdown=None) -> bytes:
  html = render_to_string("prodaja/quotes/client.html", {"quote": quote, "breakdown": breakdown})
  return _html_to_pdf_bytes(html)

def render_internal_pdf(*, quote, breakdown=None, snapshot_hash: str = "-") -> bytes:
  html = render_to_string("prodaja/quotes/internal.html", {"quote": quote, "breakdown": breakdown, "snapshot_hash": snapshot_hash})
  return _html_to_pdf_bytes(html)

# ================================

# FILE: prodaja/templates/prodaja/quotes/client.html

# ================================

"""

<!doctype html>

<html>
<head>
  <meta charset="utf-8" />
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; font-size: 12px; }
    h1 { font-size: 18px; margin-bottom: 4px; }
    table { width: 100%; border-collapse: collapse; margin: 8px 0; }
    th, td { border: 1px solid #ddd; padding: 6px; text-align: left; }
    .right { text-align: right; }
  </style>
<\/head>
<body>
  <h1>QUOTE — {{ quote.number }}<\/h1>
  <p>Customer: {{ quote.customer }}<\/p>
  <table>
    <thead><tr><th>Description<\/th><th class="right">Qty<\/th><th>UoM<\/th><th class="right">Unit<\/th><th class="right">Total<\/th><\/tr><\/thead>
    <tbody>
      {% for it in quote.items.all %}
      <tr>
        <td>{{ it.description }}<\/td>
        <td class="right">{{ it.qty }}<\/td>
        <td>{{ it.uom }}<\/td>
        <td class="right">€ {{ it.unit_price }}<\/td>
        <td class="right">€ {{ it.total }}<\/td>
      <\/tr>
      {% endfor %}
    <\/tbody>
  <\/table>
  <p><strong>Status:<\/strong> {{ quote.status }}<\/p>
<\/body>
<\/html>
"""

# ================================

# FILE: prodaja/templates/prodaja/quotes/internal.html

# ================================

"""

<!doctype html>

<html>
<head>
  <meta charset="utf-8" />
  <style>
    body { font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif; font-size: 12px; }
    h1 { font-size: 18px; margin-bottom: 4px; }
    table { width: 100%; border-collapse: collapse; margin: 8px 0; }
    th, td { border: 1px solid #ddd; padding: 6px; text-align: left; }
    .muted { color: #666; }
    .right { text-align: right; }
  </style>
<\/head>
<body>
  <h1>INTERNAL QUOTE — {{ quote.number }}<\/h1>
  <p class="muted">Snapshot hash: {{ snapshot_hash }}<\/p>
  <table>
    <thead><tr><th>Description<\/th><th>Type<\/th><th class="right">Qty<\/th><th>UoM<\/th><th class="right">Unit<\/th><th class="right">Total<\/th><\/tr><\/thead>
    <tbody>
      {% for it in quote.items.all %}
      <tr>
        <td>{{ it.description }}<\/td>
        <td>{{ it.type }}<\/td>
        <td class="right">{{ it.qty }}<\/td>
        <td>{{ it.uom }}<\/td>
        <td class="right">€ {{ it.unit_price }}<\/td>
        <td class="right">€ {{ it.total }}<\/td>
      <\/tr>
      {% endfor %}
    <\/tbody>
  <\/table>
<\/body>
<\/html>
"""

# ================================

# FILE: tests/quote/test_estimator_smoke.py

# ================================

import pytest
from decimal import Decimal
from prodaja.services.estimator.dto import QuoteInput, OptionSpec, ItemInput
from prodaja.services.estimator.engine import estimate

def test_estimator_smoke():
  qi = QuoteInput(
    tenant="demo",
    options=[
      OptionSpec(name="Good", items=[ItemInput(type="fabrication", description="Frame", qty=Decimal("10"), uom="m")]),
      OptionSpec(name="Better", items=[ItemInput(type="painting", description="Coat", qty=Decimal("20"), uom="m2")]),
    ],
    price_list={"base": Decimal("10")},
  )
  br = estimate(qi)
  assert set(br.options.keys()) == {"Good", "Better"}
  assert all(b.total > 0 for b in br.options.values())

# ================================

# FILE: tests/quote/test_api_quotes.py

# ================================

import pytest
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_quote_crud_and_estimate(api_client_factory, tenant_user_factory):
  client: APIClient = api_client_factory()
  tenant_user = tenant_user_factory()
  client.force_authenticate(user=tenant_user.user)

  ```
  # create quote
  r = client.post("/api/quotes/", {"number": "Q-001", "customer": tenant_user.tenant_customer_id}, format="json")
  assert r.status_code in (200, 201), r.content
  qid = r.json()["id"]

  # estimate
  payload = {"tenant": "demo", "options": [{"name": "Good", "items": [{"type": "fabrication", "description": "x", "qty": "5", "uom": "m"}]}], "price_list": {"base": "10"}}
  r2 = client.post("/api/quotes/estimate/", payload, format="json")
  assert r2.status_code == 200
  assert "options" in r2.json()

  # send & accept
  assert client.post(f"/api/quotes/{qid}/send/").status_code == 200
  assert client.post(f"/api/quotes/{qid}/accept/").status_code == 200
  ```

# ================================

# FILE: tests/quote/test_pdf_quotes.py

# ================================

import pytest
from prodaja.pdf.quote import render_client_pdf, render_internal_pdf

@pytest.mark.django_db
def test_quote_pdfs_smoke(quote_factory):
  q = quote_factory()
  c = render_client_pdf(quote=q)
  i = render_internal_pdf(quote=q, snapshot_hash="abc123")
  assert len(c) > 0 and len(i) > 0
