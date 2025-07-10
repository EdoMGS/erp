from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from nalozi.forms import ProjektForm
from nalozi.models import Projekt, RadniNalog


@pytest.mark.django_db
def test_projekt_status_ugrozenosti():
    projekt = Projekt.objects.create(
        naziv_projekta="Test Projekt",
        tip_projekta="izrada_vozila",
        rok_za_isporuku=timezone.now().date() + timedelta(days=5),
    )

    # Generiraj 10 radnih naloga
    for i in range(10):
        RadniNalog.objects.create(
            naziv_naloga=f"Nalog {i+1}",
            projekt=projekt,
            status="Završeno" if i < 7 else "U tijeku",  # 7 završeno, 3 u tijeku
            datum_pocetka=timezone.now().date() - timedelta(days=i * 2),
            datum_zavrsetka=(
                timezone.now().date() - timedelta(days=i) if i < 7 else None
            ),
        )

    # Ponovno izračunaj status projekta
    projekt.azuriraj_status()

    # Očekuje se da je projekt siguran (70% napretka i rok nije prošao)
    assert projekt.status_ugrozenosti() == "Siguran"

    # Promijeni rok isporuke na prošlost
    projekt.rok_za_isporuku = timezone.now().date() - timedelta(days=1)
    projekt.save()

    # Sada bi status trebao biti ugrožen
    assert projekt.status_ugrozenosti() == "Ugrožen"


@pytest.mark.django_db
def test_radni_nalog_clean_validacija():
    projekt = Projekt.objects.create(naziv_projekta="Test Projekt")

    radni_nalog = RadniNalog(
        naziv_naloga="Test Nalog",
        projekt=projekt,
        datum_pocetka=timezone.now().date(),
        datum_zavrsetka=timezone.now().date() - timedelta(days=1),
    )

    with pytest.raises(ValidationError):
        radni_nalog.clean()


class FormsTestCase(TestCase):
    def test_projekt_form_validacija(self):
        form_data = {
            "naziv_projekta": "Test Projekt",
            "rok_za_isporuku": timezone.now().date() + timedelta(days=10),
            "tip_projekta": "izrada_vozila",  # Obavezno polje
        }
        form = ProjektForm(data=form_data)
        self.assertTrue(form.is_valid())
