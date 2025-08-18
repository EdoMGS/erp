import threading

from django.utils.deprecation import MiddlewareMixin

_thread_locals = threading.local()


def set_current_tenant(tenant):
    _thread_locals.tenant = tenant


def get_current_tenant():
    return getattr(_thread_locals, 'tenant', None)


def reset_current_tenant():
    if hasattr(_thread_locals, 'tenant'):
        del _thread_locals.tenant


class ModuleInteractionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        return None


class TenantMiddleware(MiddlewareMixin):
    def process_request(self, request):
        tenant = getattr(request, 'tenant', None) or request.META.get('HTTP_X_TENANT_ID')
        set_current_tenant(tenant)
        request.tenant = tenant

    def process_response(self, request, response):
        reset_current_tenant()
        return response
