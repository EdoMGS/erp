from __future__ import annotations

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# 11-year retention window for blobstore content
RETENTION_DELTA = timedelta(days=11 * 365)


def default_retained_until():
    return timezone.now() + RETENTION_DELTA


class Blob(models.Model):
    """Immutable content-addressed blob record (WORM).
    The payload is stored on disk (or S3) under sha256 path, never updated.
    DB row acts as index and links artifact to tenant/object.
    """

    class Kind(models.TextChoices):
        INVOICE_PDF = "invoice_pdf", "Invoice PDF"
        INVOICE_UBL = "invoice_ubl", "Invoice UBL"
        JOPPD_XML = "joppd_xml", "JOPPD XML"
        OTHER = "other", "Other"

    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE)
    kind = models.CharField(max_length=32, choices=Kind.choices)

    # logical key (e.g. invoice:1234:v1)
    key = models.CharField(max_length=256)

    # content address
    sha256 = models.CharField(max_length=64, db_index=True)
    size = models.BigIntegerField()
    mimetype = models.CharField(max_length=128)

    # physical location hint (filesystem path or URL)
    uri = models.CharField(max_length=512)

    created_at = models.DateTimeField(default=timezone.now, db_index=True)
    # prevent deletion before this timestamp (11y retention)
    retained_until = models.DateTimeField(default=default_retained_until)

    class Meta:
        unique_together = ("tenant", "kind", "key")

    def __str__(self) -> str:  # pragma: no cover
        return f"Blob({self.tenant_id}, {self.kind}, {self.key}, {self.sha256[:8]}...)"

    def delete(self, *args, **kwargs):
        """Enforce WORM retention: blobs cannot be removed before 11 years."""
        if timezone.now() < self.retained_until:
            raise ValidationError("Blob is under retention")
        return super().delete(*args, **kwargs)
