from functools import wraps
from django.conf import settings

def proizvodnja_permission_required(groups=None):
    """
    Decorator that checks if user belongs to required production groups
    """
    if groups is None:
        groups = settings.PROIZVODNJA_EDIT_GROUPS

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            view_func.proizvodnja_permission_required = groups
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
