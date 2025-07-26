import pytest

from skladiste.employee_factory import create_minimal_employee
from skladiste.models import (Alat, Artikl, DnevnikDogadaja, HTZOprema,
                              Izdatnica, IzdatnicaStavka, Kategorija, Lokacija,
                              Materijal, Primka, PrimkaStavka, SkladisteResurs,
                              Zona)


@pytest.mark.django_db
def test_zona_str():
    zona = Zona.objects.create(naziv="Test Zona")
    assert str(zona) == "Test Zona"


@pytest.mark.django_db
def test_lokacija_str():
    zona = Zona.objects.create(naziv="Zona 1")
    lokacija = Lokacija.objects.create(naziv="Lokacija 1", zona=zona)
    assert str(lokacija) == "Lokacija 1"


@pytest.mark.django_db
def test_kategorija_str():
    kat = Kategorija.objects.create(naziv="Kat1")
    assert str(kat) == "Kat1"


@pytest.mark.django_db
def test_artikl_str():
    from nabava.models import Dobavljac, GrupaDobavljaca

    kat = Kategorija.objects.create(naziv="Kat1")
    zona = Zona.objects.create(naziv="Zona 1")
    lok = Lokacija.objects.create(naziv="Lokacija 1", zona=zona)
    grupa = GrupaDobavljaca.objects.create(naziv="Dummy Grupa")
    dobavljac = Dobavljac.objects.create(naziv="Dummy Dobavljac", grupa=grupa)
    artikl = Artikl.objects.create(
        naziv="Artikl1",
        sifra="A1",
        jm="kom",
        kategorija=kat,
        dobavljac=dobavljac,
        lokacija=lok,
    )
    assert str(artikl) == "Artikl1 (A1)"


@pytest.mark.django_db
def test_materijal_str():
    from nabava.models import Dobavljac, GrupaDobavljaca

    kat = Kategorija.objects.create(naziv="Kat1")
    zona = Zona.objects.create(naziv="Zona 1")
    lok = Lokacija.objects.create(naziv="Lokacija 1", zona=zona)
    grupa = GrupaDobavljaca.objects.create(naziv="Dummy Grupa")
    dobavljac = Dobavljac.objects.create(naziv="Dummy Dobavljac", grupa=grupa)
    artikl = Artikl.objects.create(
        naziv="Artikl1",
        sifra="A1",
        jm="kom",
        kategorija=kat,
        dobavljac=dobavljac,
        lokacija=lok,
    )
    materijal = Materijal.objects.create(artikl=artikl, naziv="Materijal1", cijena=1, kolicina=1)
    assert str(materijal) == "Materijal1"


@pytest.mark.django_db
def test_alat_str():
    alat = Alat.objects.create(naziv="Alat1", inventarski_broj="INV1")
    assert str(alat) == "Alat1"


@pytest.mark.django_db
def test_htzoprema_str():
    htz = HTZOprema.objects.create(vrsta="Kaciga", stanje="Novo")
    assert str(htz) == "Kaciga - Novo"


@pytest.mark.django_db
def test_dnevnikdogadaja_str():
    from nabava.models import Dobavljac, GrupaDobavljaca

    kat = Kategorija.objects.create(naziv="Kat1")
    zona = Zona.objects.create(naziv="Zona 1")
    lok = Lokacija.objects.create(naziv="Lokacija 1", zona=zona)
    grupa = GrupaDobavljaca.objects.create(naziv="Dummy Grupa")
    dobavljac = Dobavljac.objects.create(naziv="Dummy Dobavljac", grupa=grupa)
    artikl = Artikl.objects.create(
        naziv="Artikl1",
        sifra="A1",
        jm="kom",
        kategorija=kat,
        dobavljac=dobavljac,
        lokacija=lok,
    )
    dog = DnevnikDogadaja.objects.create(dogadaj="Test", artikl=artikl)
    assert str(dog).endswith("- Test")


@pytest.mark.django_db
def test_skladisteresurs_str():
    res = SkladisteResurs.objects.create(naziv="Res1", kolicina=1, lokacija="A")
    assert str(res) == "Res1"


@pytest.mark.django_db
def test_primka_str():
    from django.contrib.auth import get_user_model

    from nabava.models import Dobavljac, GrupaDobavljaca

    User = get_user_model()
    user = User.objects.create(username="testuser")
    grupa = GrupaDobavljaca.objects.create(naziv="Dummy Grupa")
    dobavljac = Dobavljac.objects.create(naziv="Dummy Dobavljac", grupa=grupa)
    primka = Primka.objects.create(broj_primke="P1", datum="2024-01-01", dobavljac=dobavljac, created_by=user)
    assert "Primka P1" in str(primka)


@pytest.mark.django_db
def test_primkastavka_str():
    from django.contrib.auth import get_user_model

    from nabava.models import Dobavljac, GrupaDobavljaca

    User = get_user_model()
    user = User.objects.create(username="testuser")
    grupa = GrupaDobavljaca.objects.create(naziv="Dummy Grupa")
    dobavljac = Dobavljac.objects.create(naziv="Dummy Dobavljac", grupa=grupa)
    kat = Kategorija.objects.create(naziv="Kat1")
    zona = Zona.objects.create(naziv="Zona 1")
    lok = Lokacija.objects.create(naziv="Lokacija 1", zona=zona)
    artikl = Artikl.objects.create(
        naziv="Artikl1",
        sifra="A1",
        jm="kom",
        kategorija=kat,
        dobavljac=dobavljac,
        lokacija=lok,
    )
    primka = Primka.objects.create(broj_primke="P1", datum="2024-01-01", dobavljac=dobavljac, created_by=user)
    stavka = PrimkaStavka.objects.create(primka=primka, artikl=artikl, kolicina=1, cijena=1)
    assert artikl.naziv in str(stavka)


@pytest.mark.django_db
def test_izdatnica_str():
    from django.contrib.auth import get_user_model

    User = get_user_model()
    user = User.objects.create(username="testuser")
    employee = create_minimal_employee(user)
    izdatnica = Izdatnica.objects.create(broj_izdatnice="I1", datum="2024-01-01", preuzeo=employee, created_by=user)
    assert "Izdatnica I1" in str(izdatnica)


@pytest.mark.django_db
def test_izdatnicastavka_str():
    from django.contrib.auth import get_user_model

    from nabava.models import Dobavljac, GrupaDobavljaca

    User = get_user_model()
    user = User.objects.create(username="testuser")
    employee = create_minimal_employee(user)
    grupa = GrupaDobavljaca.objects.create(naziv="Dummy Grupa")
    dobavljac = Dobavljac.objects.create(naziv="Dummy Dobavljac", grupa=grupa)
    kat = Kategorija.objects.create(naziv="Kat1")
    zona = Zona.objects.create(naziv="Zona 1")
    lok = Lokacija.objects.create(naziv="Lokacija 1", zona=zona)
    artikl = Artikl.objects.create(
        naziv="Artikl1",
        sifra="A1",
        jm="kom",
        kategorija=kat,
        dobavljac=dobavljac,
        lokacija=lok,
    )
    izdatnica = Izdatnica.objects.create(broj_izdatnice="I1", datum="2024-01-01", preuzeo=employee, created_by=user)
    stavka = IzdatnicaStavka.objects.create(izdatnica=izdatnica, artikl=artikl, kolicina=1)
    assert artikl.naziv in str(stavka)
