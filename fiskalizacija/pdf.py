from __future__ import annotations

import hashlib


def build_pdf(xml: str, jir: str) -> bytes:
    """Return a tiny PDF-like payload embedding QR and hash metadata."""
    h = hashlib.sha256(xml.encode()).hexdigest()
    content = f"%PDF-1.4\nJIR:{jir}\nQR:{jir}\nHASH:{h}\n%%EOF"
    return content.encode()
