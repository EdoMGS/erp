from django.http import HttpResponseBadRequest
from django.utils.deprecation import MiddlewareMixin


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # Extract tenant from subdomain or header
        tenant = request.META.get("HTTP_X_TENANT")
        if not tenant:
            return HttpResponseBadRequest("Tenant header is missing.")

        # Attach tenant to request for further processing
        request.tenant = tenant
