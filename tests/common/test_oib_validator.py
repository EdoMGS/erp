import pytest
from django.core.exceptions import ValidationError

from client.models import ClientSupplier
from common.validators import validate_oib


def test_validate_oib_accepts_valid_number():
    validate_oib("12345678903")  # should not raise


def test_validate_oib_rejects_invalid_number():
    with pytest.raises(ValidationError):
        validate_oib("12345678901")


@pytest.mark.django_db
def test_client_supplier_model_uses_validator():
    client = ClientSupplier(
        name="X",
        address="A",
        email="x@example.com",
        phone="012345678",
        oib="12345678901",
        city="Zagreb",
        postal_code="10000",
    )
    with pytest.raises(ValidationError):
        client.full_clean()
