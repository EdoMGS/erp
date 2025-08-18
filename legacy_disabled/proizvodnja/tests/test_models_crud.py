import pytest
from django.utils import timezone
from decimal import Decimal

from ljudski_resursi.models import Nagrada
from proizvodnja.models import RadniNalog
from skladiste.models import Materijal

from tests.factories import (
    create_work_order,
    create_material,
)


@pytest.mark.django_db
def test_radninalog_crud():
    rn = create_work_order()
    assert RadniNalog.objects.filter(pk=rn.pk).exists()
    original_pk = rn.pk
    rn.naziv_naloga = "Izmijenjen nalog"
    rn.save(update_fields=["naziv_naloga"])
    assert RadniNalog.objects.get(pk=original_pk).naziv_naloga == "Izmijenjen nalog"
    rn.delete()
    assert not RadniNalog.objects.filter(pk=original_pk).exists()


@pytest.mark.django_db
def test_materijal_crud():
    m = create_material()
    assert Materijal.objects.filter(pk=m.pk).exists()
    m.naziv = "Izmijenjen materijal"
    m.save(update_fields=["naziv"])
    assert Materijal.objects.get(pk=m.pk).naziv == "Izmijenjen materijal"
    m.delete()
    assert not Materijal.objects.filter(pk=m.pk).exists()


@pytest.mark.django_db
def test_nagrada_crud():
    rn = create_work_order()
    emp = rn.employee  # reuse created employee
    n = Nagrada.objects.create(employee=emp, radni_nalog=rn, iznos=100)
    assert Nagrada.objects.filter(pk=n.pk).exists()
    n.iznos = Decimal("200")
    n.save(update_fields=["iznos"])
    assert Nagrada.objects.get(pk=n.pk).iznos == 200
    n.delete()
    assert not Nagrada.objects.filter(pk=n.pk).exists()
