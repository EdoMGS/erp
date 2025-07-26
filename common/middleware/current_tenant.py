from django.utils.deprecation import MiddlewareMixin

from tenants.models import Tenant


class CurrentTenantMiddleware(MiddlewareMixin):
    """
    Middleware to set the current tenant based on the domain or request header.
    """

    def process_request(self, request):
        domain = request.META.get("HTTP_HOST", "").split(":")[0]
        tenant = Tenant.objects.filter(domain=domain).first()
        if tenant:
            request.tenant = tenant
        else:
            request.tenant = None
