from rest_framework import viewsets

from .models import Invoice
from .serializers import InvoiceSerializer


class TenantQuerysetMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        tenant = getattr(self.request, "tenant", None)
        return qs.filter(tenant=tenant) if tenant else qs.none()


class InvoiceViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
