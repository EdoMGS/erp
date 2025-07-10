from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect


class ProizvodnjaAccessMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/proizvodnja/'):
            if not request.user.is_authenticated:
                return redirect(f"{settings.LOGIN_URL}?next={request.path}")
            
            if not getattr(request.user, 'employee', None):
                messages.error(request, 'Potreban je profil zaposlenika.')
                return redirect('human-resources:employee-setup')
        
        return self.get_response(request)

    def process_view(self, request, view_func, view_args, view_kwargs):
        if hasattr(view_func, 'proizvodnja_permission_required'):
            required_groups = settings.PROIZVODNJA_ALLOWED_GROUPS.get('EDIT', [])
            if not request.user.groups.filter(name__in=required_groups).exists():
                messages.error(request, 'Nemate potrebna prava pristupa.')
                return redirect('dashboard')
        return None
