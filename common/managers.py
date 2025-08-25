from django.db import models


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class TenantManager(models.Manager):
    """Lightweight multi-tenant helper manager.

    Provides a convenience ``for_tenant(tenant)`` to filter by a "tenant"
    or "tenant_id" foreign key field when present. Falls back to the base
    queryset if no such field exists on the model.
    """

    def for_tenant(self, tenant):
        if tenant is None:
            return self.get_queryset().none()

        # Try common field names first
        field_names = {f.name for f in self.model._meta.get_fields()}
        if "tenant" in field_names:
            return self.get_queryset().filter(tenant=tenant)
        if "tenant_id" in field_names:
            return self.get_queryset().filter(tenant_id=tenant)

        # No tenant field on this model; return unfiltered queryset
        return self.get_queryset()
