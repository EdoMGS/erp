from datetime import timedelta

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone

from common import blobstore
from common.models.blob import Blob
from tenants.models import Tenant


@pytest.mark.django_db
def test_worm_put_get(tmp_path):
    settings.BLOBSTORE_ROOT = tmp_path
    tenant = Tenant.objects.create(name="T", domain="t.test")
    data = b"hello pdf"
    blob, created = blobstore.put_immutable(
        tenant=tenant,
        kind="invoice_pdf",
        key="invoice:1:v1",
        data=data,
        mimetype="application/pdf",
    )
    assert created is True
    blob2, created2 = blobstore.put_immutable(
        tenant=tenant,
        kind="invoice_pdf",
        key="invoice:1:v1",
        data=b"something else",
        mimetype="application/pdf",
    )
    assert created2 is False
    assert blob.sha256 == blob2.sha256
    got = blobstore.get(tenant=tenant, kind="invoice_pdf", key="invoice:1:v1")
    assert got == data


@pytest.mark.django_db
def test_blob_is_content_addressed(tmp_path):
    settings.BLOBSTORE_ROOT = tmp_path
    tenant = Tenant.objects.create(name="T", domain="t.test")
    d1 = b"a" * 10
    d2 = b"a" * 10
    b1, _ = blobstore.put_immutable(
        tenant=tenant,
        kind="other",
        key="k1",
        data=d1,
        mimetype="application/octet-stream",
    )
    b2, _ = blobstore.put_immutable(
        tenant=tenant,
        kind="other",
        key="k2",
        data=d2,
        mimetype="application/octet-stream",
    )
    assert b1.sha256 == b2.sha256


@pytest.mark.django_db
def test_blob_retention_blocks_delete(tmp_path):
    settings.BLOBSTORE_ROOT = tmp_path
    tenant = Tenant.objects.create(name="T", domain="t.test")
    blob, _ = blobstore.put_immutable(
        tenant=tenant,
        kind="other",
        key="k1",
        data=b"x",
        mimetype="application/octet-stream",
    )
    with pytest.raises(ValidationError):
        blob.delete()

    # Simulate old blob past retention period
    Blob.objects.filter(id=blob.id).update(
        created_at=timezone.now() - timedelta(days=365 * 12),
        retained_until=timezone.now() - timedelta(days=1),
    )
    blob.refresh_from_db()
    blob.delete()
    assert not Blob.objects.filter(id=blob.id).exists()
