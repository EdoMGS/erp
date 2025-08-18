import pytest
from uuid import uuid4
from django.contrib.auth import get_user_model
from django.utils import timezone

from ljudski_resursi.models import Employee, Nagrada
from proizvodnja.models import RadniNalog
from skladiste.models import Materijal


# ---------------------------------------------------------------------------
# Helper factory functions (kept here for now; can be moved to conftest later)
# They intentionally import models lazily inside to avoid circular import traps.
# ---------------------------------------------------------------------------
def factory_financial_details():
    from financije.models import FinancialDetails

    return FinancialDetails.objects.create()


def factory_projekt():
    from proizvodnja.models import Projekt

    fd = factory_financial_details()
    return Projekt.objects.create(naziv_projekta=f"Projekt-{uuid4().hex[:6]}", financial_details=fd)


def factory_proizvodnja():
    from proizvodnja.models import Proizvodnja

    projekt = factory_projekt()
    return Proizvodnja.objects.create(projekt=projekt, naziv=f"Proizvodnja-{uuid4().hex[:6]}")


def factory_employee(username_prefix="emp"):
    User = get_user_model()
    user = User.objects.create(username=f"{username_prefix}-{uuid4().hex[:6]}")
    return Employee.objects.create(user=user)


def factory_radninalog():
    proizvodnja = factory_proizvodnja()
    employee = factory_employee()
    # broj_naloga mora biti jedinstven
    return RadniNalog.objects.create(
        naziv_naloga=f"RN-{uuid4().hex[:6]}",
        broj_naloga=f"BN-{uuid4().hex[:10]}",
        status="OTVOREN",
        prioritet="visok",
        tip_posla="instalacija",
        datum_pocetka=timezone.now().date(),
        proizvodnja=proizvodnja,
        employee=employee,
    )


def factory_artikl_chain():
    """Create full dependency chain for Artikl -> Materijal."""
    from skladiste.models import Kategorija, Lokacija, Artikl
    from nabava.models import GrupaDobavljaca, Dobavljac

    grupa = GrupaDobavljaca.objects.create(naziv=f"Grupa-{uuid4().hex[:6]}")
    dobavljac = Dobavljac.objects.create(
        naziv=f"Dob-{uuid4().hex[:6]}",
        oib=str(uuid4().int)[:11],
        adresa="Adresa 1",
        grad="Grad",
        drzava="HR",
        email=f"sup-{uuid4().hex[:6]}@ex.com",
        telefon="123",
        grupa=grupa,
    )
    kategorija = Kategorija.objects.create(naziv=f"Kat-{uuid4().hex[:6]}")
    lokacija = Lokacija.objects.create(naziv=f"Lok-{uuid4().hex[:6]}")
    artikl = Artikl.objects.create(
        naziv=f"Artikl-{uuid4().hex[:6]}",
        sifra=uuid4().hex[:12],
        jm="kom",
        kategorija=kategorija,
        dobavljac=dobavljac,
        lokacija=lokacija,
    )
    return artikl


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_radninalog_crud():
    rn = factory_radninalog()
    assert RadniNalog.objects.filter(pk=rn.pk).exists()
    original_pk = rn.pk
    rn.naziv_naloga = "Izmijenjen nalog"
    rn.save(update_fields=["naziv_naloga"])
    assert RadniNalog.objects.get(pk=original_pk).naziv_naloga == "Izmijenjen nalog"
    rn.delete()
    assert not RadniNalog.objects.filter(pk=original_pk).exists()


@pytest.mark.django_db
def test_materijal_crud():
    from skladiste.models import Artikl

    artikl = factory_artikl_chain()
    m = Materijal.objects.create(
        naziv="Test materijal",
        artikl=artikl,
        cijena=10,
        kolicina=5,
    )
    assert Materijal.objects.filter(pk=m.pk).exists()
    m.naziv = "Izmijenjen materijal"
    m.save(update_fields=["naziv"])
    assert Materijal.objects.get(pk=m.pk).naziv == "Izmijenjen materijal"
    m.delete()
    assert not Materijal.objects.filter(pk=m.pk).exists()


@pytest.mark.django_db
def test_nagrada_crud():
    rn = factory_radninalog()
    emp = rn.employee  # reuse already created employee
    n = Nagrada.objects.create(employee=emp, radni_nalog=rn, iznos=100)
    assert Nagrada.objects.filter(pk=n.pk).exists()
    n.iznos = 200
    n.save(update_fields=["iznos"])
    assert Nagrada.objects.get(pk=n.pk).iznos == 200
    n.delete()
    assert not Nagrada.objects.filter(pk=n.pk).exists()
