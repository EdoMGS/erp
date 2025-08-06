from django.db import models
from common.middleware import get_current_tenant


class TenantManager(models.Manager):
    """Automatski filter za tenante."""

    def get_queryset(self):
        qs = super().get_queryset()
        tenant = get_current_tenant()
        if tenant is None:
            return qs
        return qs.filter(tenant_id=tenant)
