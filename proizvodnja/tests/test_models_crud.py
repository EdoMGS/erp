import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from ljudski_resursi.models import Employee, Nagrada
from proizvodnja.models import RadniNalog
from skladiste.models import Materijal


@pytest.mark.django_db
def test_radninalog_crud():
    rn = RadniNalog.objects.create(
        naziv_naloga="Test nalog",
        status="OTVOREN",
        prioritet="visok",
        tip_posla="instalacija",
        datum_pocetka=timezone.now().date(),
    )
    assert RadniNalog.objects.filter(pk=rn.pk).exists()
    rn.naziv_naloga = "Izmijenjen nalog"
    rn.save()
    assert RadniNalog.objects.get(pk=rn.pk).naziv_naloga == "Izmijenjen nalog"
    rn.delete()
    assert not RadniNalog.objects.filter(pk=rn.pk).exists()


@pytest.mark.django_db
def test_materijal_crud():
    from skladiste.models import Artikl

    artikl = Artikl.objects.create(naziv="Test artikl")
    m = Materijal.objects.create(naziv="Test materijal", artikl=artikl, cijena=10, kolicina=5)
    assert Materijal.objects.filter(pk=m.pk).exists()
    m.naziv = "Izmijenjen materijal"
    m.save()
    assert Materijal.objects.get(pk=m.pk).naziv == "Izmijenjen materijal"
    m.delete()
    assert not Materijal.objects.filter(pk=m.pk).exists()


@pytest.mark.django_db
def test_nagrada_crud():
    user = get_user_model().objects.create(username="emp1")
    emp = Employee.objects.create(user=user)
    rn = RadniNalog.objects.create(
        naziv_naloga="Test nalog",
        status="OTVOREN",
        prioritet="visok",
        tip_posla="instalacija",
        datum_pocetka=timezone.now().date(),
    )
    n = Nagrada.objects.create(employee=emp, radni_nalog=rn, iznos=100)
    assert Nagrada.objects.filter(pk=n.pk).exists()
    n.iznos = 200
    n.save()
    assert Nagrada.objects.get(pk=n.pk).iznos == 200
    n.delete()
    assert not Nagrada.objects.filter(pk=n.pk).exists()
