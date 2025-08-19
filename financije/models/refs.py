from django.db import models
from tenants.models import Tenant
from .accounting import JournalEntry


class PostedJournalRef(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    ref = models.CharField(max_length=64)
    kind = models.CharField(max_length=32, default="generic")
    entry = models.OneToOneField(JournalEntry, on_delete=models.CASCADE, related_name="posted_ref")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'financije'
        unique_together = ("tenant", "ref", "kind")
        indexes = [models.Index(fields=["tenant", "ref", "kind"])]

    def __str__(self):
        return f"{self.tenant_id}:{self.kind}:{self.ref}"
