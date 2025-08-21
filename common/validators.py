import re
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_oib(value):
    if not re.match(r"^\d{11}$", value):
        raise ValidationError(_("OIB must be exactly 11 digits"))


def validate_phone(value):
    if not re.match(r"^\+?[\d\s-]{8,}$", value):
        raise ValidationError(_("Invalid phone number format"))


def validate_positive_decimal(value):
    if value <= 0:
        raise ValidationError(_("Value must be greater than zero"))


class CommonValidator:
    @staticmethod
    def validate_financial_data(value: Any) -> None:
        if value < 0:
            raise ValidationError(_("Value cannot be negative"))

    @staticmethod
    def validate_status_transition(
        current_status: str, new_status: str, allowed_transitions: dict
    ) -> None:
        if new_status not in allowed_transitions.get(current_status, []):
            raise ValidationError(_("Invalid status transition"))
