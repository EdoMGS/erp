import re
from typing import Any

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def is_valid_oib(oib: str) -> bool:
    """Return True if the OIB passes checksum validation."""

    oib = "".join(ch for ch in str(oib) if ch.isdigit())
    if len(oib) != 11:
        return False
    a = 10
    for i in range(10):
        a = (int(oib[i]) + a) % 10
        if a == 0:
            a = 10
        a = (a * 2) % 11
    control = (11 - a) % 10
    return control == int(oib[-1])


def validate_oib(value):
    """Validate Croatian OIB with control digit.

    Uses the algorithm defined by the Croatian Tax Administration. The last
    digit of the 11‑digit OIB is a check digit calculated from the preceding
    ten digits. Any deviation raises :class:`ValidationError`.
    """

    if not re.fullmatch(r"\d{11}", value or ""):
        raise ValidationError(_("OIB must be exactly 11 digits"))
    if not is_valid_oib(value):
        raise ValidationError(_("Invalid OIB checksum"))


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
