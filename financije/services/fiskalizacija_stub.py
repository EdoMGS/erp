import hashlib
import json
from dataclasses import dataclass

AUDIT_LOG: list[dict] = []


def _compute_zki(number: str, issued_at, net: str, operator_mark: str) -> str:
    seed = f"{number}|{issued_at}|{net}|{operator_mark}"
    return hashlib.sha1(seed.encode()).hexdigest()


@dataclass
class FiscalizationResult:
    zki: str
    jir: str
    qr: str


def fiscalize(invoice) -> FiscalizationResult:
    """Fake fiscalization service.

    Generates deterministic ZKI, simulates JIR response and records an
    audit log with request/response hashes. Returns QR payload string that
    can be embedded into PDFs.
    """

    payload = {
        "number": invoice.number,
        "issued_at": invoice.issued_at.isoformat(),
        "net": str(invoice.net_total),
        "operator": invoice.operator_mark,
    }
    req_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    zki = _compute_zki(invoice.number, payload["issued_at"], payload["net"], invoice.operator_mark)
    jir = hashlib.sha1((zki + "jir").encode()).hexdigest()
    qr = json.dumps({"n": invoice.number, "zki": zki, "jir": jir})
    resp_hash = hashlib.sha256(
        json.dumps({"jir": jir, "zki": zki}, sort_keys=True).encode()
    ).hexdigest()
    AUDIT_LOG.append({"request_hash": req_hash, "response_hash": resp_hash})
    return FiscalizationResult(zki=zki, jir=jir, qr=qr)


__all__ = ["fiscalize", "FiscalizationResult", "AUDIT_LOG"]
