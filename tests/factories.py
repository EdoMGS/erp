"""Central lightweight test factories (manual, no factory-boy dependency yet)."""
from __future__ import annotations

from uuid import uuid4
from decimal import Decimal
from django.contrib.auth import get_user_model


def create_financial_details():
    from financije.models import FinancialDetails
    return FinancialDetails.objects.create()


def create_project():
    from proizvodnja.models import Projekt
    fd = create_financial_details()
    return Projekt.objects.create(naziv_projekta=f"Projekt-{uuid4().hex[:6]}", financial_details=fd)


def create_production():
    from proizvodnja.models import Proizvodnja
    projekt = create_project()
    return Proizvodnja.objects.create(projekt=projekt, naziv=f"Proizvodnja-{uuid4().hex[:6]}")


def create_employee(username_prefix: str = "emp"):
    from ljudski_resursi.models import Employee
    User = get_user_model()
    user = User.objects.create(username=f"{username_prefix}-{uuid4().hex[:8]}")
    return Employee.objects.create(user=user)


def create_work_order():
    from proizvodnja.models import RadniNalog
    production = create_production()
    employee = create_employee()
    return RadniNalog.objects.create(
        naziv_naloga=f"RN-{uuid4().hex[:6]}",
        broj_naloga=f"BN-{uuid4().hex[:10]}",
        status="OTVOREN",
        prioritet="visok",
        tip_posla="instalacija",
        datum_pocetka=None,
        proizvodnja=production,
        employee=employee,
    )


def create_artikl_chain():
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


def create_material(naziv: str = "Test materijal", cijena: Decimal = Decimal("10"), kolicina: Decimal = Decimal("5")):
    from skladiste.models import Materijal
    artikl = create_artikl_chain()
    return Materijal.objects.create(
        naziv=naziv,
        artikl=artikl,
        cijena=cijena,
        kolicina=kolicina,
    )
