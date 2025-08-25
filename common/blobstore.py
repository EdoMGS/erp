from __future__ import annotations

import hashlib
import os
from pathlib import Path

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models.blob import RETENTION_DELTA, Blob

ROOT = Path(getattr(settings, "BLOBSTORE_ROOT", "/var/erp/blobstore"))


def _bucket_for(digest: str) -> Path:
    # shard by first 4+2 hex chars
    return ROOT / digest[:2] / digest[2:4]


def _safe_write(dst: Path, data: bytes) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    tmp = dst.with_suffix(".tmp")
    with open(tmp, "wb") as f:
        f.write(data)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, dst)


@transaction.atomic
def put_immutable(*, tenant, kind: str, key: str, data: bytes, mimetype: str) -> tuple[Blob, bool]:
    """Store bytes immutably. If (tenant,kind,key) exists → return existing, do not overwrite.
    Returns (Blob, created_flag)
    """
    # check existing logical key
    try:
        existing = Blob.objects.get(tenant=tenant, kind=kind, key=key)
        return existing, False
    except Blob.DoesNotExist:
        pass

    sha256 = hashlib.sha256(data).hexdigest()
    bucket = _bucket_for(sha256)
    filename = bucket / sha256

    # write only if not already present (content-addressed de-dup)
    if not filename.exists():
        _safe_write(filename, data)

    blob = Blob.objects.create(
        tenant=tenant,
        kind=kind,
        key=key,
        sha256=sha256,
        size=len(data),
        mimetype=mimetype,
        uri=str(filename),
        retained_until=timezone.now() + RETENTION_DELTA,
    )
    return blob, True


def get(*, tenant, kind: str, key: str) -> bytes:
    blob = Blob.objects.get(tenant=tenant, kind=kind, key=key)
    p = Path(blob.uri)
    return p.read_bytes()
