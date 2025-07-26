from django.db import models
from django.utils.timezone import now


class ComplianceDocument(models.Model):
    ZNR = "ZNR"
    PZO = "PZO"
    INSURANCE = "INS"

    DOCUMENT_TYPES = [
        (ZNR, "ZNR"),
        (PZO, "PZO"),
        (INSURANCE, "Insurance"),
    ]

    name = models.CharField(max_length=255)
    document_type = models.CharField(max_length=3, choices=DOCUMENT_TYPES)
    expiry_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_expired(self):
        return self.expiry_date < now().date()

    def __str__(self):
        return f"{self.name} ({self.document_type})"
