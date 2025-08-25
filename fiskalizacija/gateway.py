from __future__ import annotations

import hashlib


def send_invoice(xml: str) -> dict[str, str]:
    """Stub sandbox gateway producing deterministic JIR/ZKI codes."""
    zki = hashlib.sha1(xml.encode()).hexdigest()
    jir = hashlib.sha1(zki.encode()).hexdigest()
    return {"jir": jir, "zki": zki, "status": "OK"}
