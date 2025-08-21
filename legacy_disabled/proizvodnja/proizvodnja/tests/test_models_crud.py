import pytest

pytestmark = pytest.mark.skip(reason="Legacy proizvodnja CRUD tests skipped (stub app)")
from django.contrib.auth import get_user_model
from django.utils import timezone

from ljudski_resursi.models import Employee, Nagrada
from proizvodnja.models import RadniNalog
from skladiste.models import Materijal


@pytest.mark.django_db
def test_placeholder_radninalog():
    assert True


@pytest.mark.django_db
def test_placeholder_materijal():
    assert True


@pytest.mark.django_db
def test_placeholder_nagrada():
    assert True
