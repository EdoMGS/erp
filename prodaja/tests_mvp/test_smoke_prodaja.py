import pytest
from prodaja.models import SalesOpportunity


@pytest.mark.django_db
def test_sales_opportunity_create():
    obj = SalesOpportunity.objects.create(name="Test", amount=10, client_name="C")
    assert obj.pk is not None
