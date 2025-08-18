import pytest
from ljudski_resursi.models import LocationConfig


@pytest.mark.django_db
def test_location_config_create():
    cfg = LocationConfig.objects.create(location_name="Loc1")
    assert cfg.pk is not None
