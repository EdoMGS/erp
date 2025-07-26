from decimal import Decimal

from django.core.exceptions import ValidationError


def validate_positive_amount(value):
    if value <= Decimal("0"):
        raise ValidationError("Amount must be positive")


def format_currency(amount):
    return f"{amount:.2f} €"


def calculate_vat(amount, rate=Decimal("25.00")):
    return (amount * rate) / Decimal("100.00")
