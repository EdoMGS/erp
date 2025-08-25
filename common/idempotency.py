from __future__ import annotations

import hashlib
import json
from typing import Any

from django.db import IntegrityError, transaction

from tenants.models import Tenant

from .models import ApiIdempotency


def compute_request_hash(data: dict | list | None) -> str | None:
    if data is None:
        return None
    try:
        payload = json.dumps(data, sort_keys=True, default=str)
    except Exception:
        payload = json.dumps(str(data))
    return hashlib.sha256(payload.encode()).hexdigest()


def get_or_create_cached_response(
    *, tenant: Tenant, path: str, method: str, key: str, request_hash: str | None
) -> tuple[dict[str, Any] | None, int | None]:
    try:
        rec = ApiIdempotency.objects.get(tenant=tenant, path=path, method=method, key=key)
        return rec.response_body, rec.status_code
    except ApiIdempotency.DoesNotExist:
        return None, None


def persist_response(
    *,
    tenant: Tenant,
    path: str,
    method: str,
    key: str,
    request_hash: str | None,
    response: dict,
    status_code: int,
) -> None:
    try:
        with transaction.atomic():
            ApiIdempotency.objects.create(
                tenant=tenant,
                path=path,
                method=method,
                key=key,
                request_hash=request_hash,
                response_body=response,
                status_code=status_code,
            )
    except IntegrityError:
        # Someone beat us to it; ignore
        pass


def verify_hmac_rotation(
    secrets: list[str], payload: str, provided_hex: str, *, algo: str = "sha256"
) -> bool:
    import hashlib
    import hmac

    for secret in secrets:
        dig = hmac.new(secret.encode(), payload.encode(), getattr(hashlib, algo)).hexdigest()
        try:
            if hmac.compare_digest(dig, provided_hex):
                return True
        except Exception:
            continue
    return False
