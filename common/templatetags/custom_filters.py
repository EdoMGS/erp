from django import template

register = template.Library()


@register.filter
def get_display_value(instance, field_name):
    """
    Pokušava pozvati metodu 'get_<field_name>_display' na danom instance objektu.
    Ako ta metoda postoji (što je slučaj kod polja s choices), vraća njen rezultat.
    Inače, vraća sirovu vrijednost polja.
    """
    method_name = f"get_{field_name}_display"
    if hasattr(instance, method_name):
        method = getattr(instance, method_name)
        return method()
    return getattr(instance, field_name, "")


@register.filter
def in_list(value, lst):
    """Provjerava je li `value` u `lst`."""
    if not isinstance(lst, (list, tuple, set)):
        return False
    return value in lst


@register.filter(name="yes_no")
def yes_no(value):
    """Prikazuje 'Da' za True i 'Ne' za False."""
    return "Da" if value else "Ne"


@register.filter(name="add_class")
def add_class(field, css_class):
    """Dodaje CSS klasu polju forme."""
    try:
        return field.as_widget(attrs={"class": css_class})
    except AttributeError:
        return field


@register.filter(name="add_placeholder")
def add_placeholder(field, placeholder_text):
    """Dodaje placeholder atribut polju forme."""
    try:
        return field.as_widget(attrs={"placeholder": placeholder_text})
    except AttributeError:
        return field


@register.filter(name="add_attributes")
def add_attributes(field, attributes):
    """Dodaje više atributa polju forme."""
    attrs = {}
    try:
        for attr in attributes.split(","):
            key, value = attr.split("=", 1)
            attrs[key.strip()] = value.strip()
        return field.as_widget(attrs=attrs)
    except (ValueError, AttributeError):
        return field


@register.filter(name="currency")
def currency(value, currency_symbol="€"):
    """Formatira numeričku vrijednost u valutu."""
    try:
        val = float(value)
        return f"{val:,.2f} {currency_symbol}"
    except (TypeError, ValueError):
        return value


@register.filter(name="split")
def split(value, delimiter=" "):
    """Splituje string na osnovu delimitera."""
    try:
        return value.split(delimiter)
    except AttributeError:
        return value


@register.filter(name="status_to_class")
def status_to_class(status):
    """Mapira status na Bootstrap klasu."""
    return {
        "ZAVRSENO": "success",
        "U_TIJEKU": "info",
        "OTKAZANO": "danger",
        "CEKANJE": "warning",
    }.get(str(status).upper(), "secondary")


@register.filter(name="hasattr")
def has_attr(obj, attr_name):
    """Vraća True/False ovisno o tome ima li 'obj' atribut 'attr_name'."""
    return hasattr(obj, attr_name)
