from django import template

register = template.Library()


@register.filter
def status_badge_class(status):
    status_classes = {
        "OTVOREN": "badge-info",
        "U_TIJEKU": "badge-primary",
        "ZAVRSENO": "badge-success",
        "PROBIJEN_ROK": "badge-danger",
    }
    return status_classes.get(status, "badge-secondary")
