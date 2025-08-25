from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any


def acceptance_hash(secret: str, snapshot_data: dict[str, Any]) -> str:
    payload = json.dumps(snapshot_data, sort_keys=True)
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def verify_acceptance_hash(secret: str, snapshot_data: dict[str, Any], provided: str) -> bool:
    expected = acceptance_hash(secret, snapshot_data)
    try:
        # constant-time compare
        return hmac.compare_digest(expected, provided)
    except Exception:
        return False
