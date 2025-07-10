# your_app/templatetags/query_transform.py
from django import template

register = template.Library()

@register.simple_tag
def query_transform(request, **kwargs):
    """
    A template tag to update query parameters.
    It removes the 'page' parameter and updates with the new ones provided.
    """
    updated = request.GET.copy()
    for k, v in kwargs.items():
        updated[k] = v
    if 'page' in updated:
        del updated['page']
    return updated.urlencode()
