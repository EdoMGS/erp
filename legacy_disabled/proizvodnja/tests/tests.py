from datetime import timedelta

import pytest
from django.utils import timezone
from nalozi.models import Materijal, Projekt, RadniNalog


@pytest.mark.django_db
def test_projekt_status_ugrozenosti():
    projekt = Projekt.objects.create(
        naziv_projekta="Test Projekt",
        tip_projekta="izrada_vozila",
        rok_za_isporuku=timezone.now().date() + timedelta(days=5),
    )
    assert projekt.status_ugrozenosti() == "Siguran"

    projekt.rok_za_isporuku = timezone.now().date() - timedelta(days=1)
    projekt.save()
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


@pytest.mark.django_db
def test_materijal_unique_together():
    projekt = Projekt.objects.create(naziv_projekta="Test Projekt")
    Materijal.objects.create(naziv="Materijal 1", projekt=projekt)
    with pytest.raises(Exception):  # Provjera jedinstvenosti
        Materijal.objects.create(naziv="Materijal 1", projekt=projekt)


from django.test import Client, TestCase
from django.urls import reverse
from nalozi.models import Projekt, RadniNalog


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.projekt = Projekt.objects.create(
            naziv_projekta="Test Projekt",
            rok_za_isporuku=timezone.now().date() + timezone.timedelta(days=10),
        )
        self.url = reverse("lista_radnih_naloga", kwargs={"projekt_id": self.projekt.id})

    def test_lista_radnih_naloga(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_filtriranje_radnih_naloga(self):
        RadniNalog.objects.create(
            naziv_naloga="Filtriran Nalog",
            projekt=self.projekt,
            funkcija_grupa="Bravarski",
        )
        response = self.client.get(self.url, {"grupa_posla": "Bravarski"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Filtriran Nalog")


from django.test import TestCase
from nalozi.forms import ProjektForm, TehnickaDokumentacijaForm


class FormsTestCase(TestCase):
    def test_projekt_form_validacija(self):
        form_data = {
            "naziv_projekta": "Test Projekt",
            "rok_za_isporuku": timezone.now().date() + timezone.timedelta(days=10),
        }
        form = ProjektForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_tehnicka_dokumentacija_clean(self):
        form_data = {
            "naziv": "Dokumentacija",
            "status": "Kompletna",
            "poveznica": "",
        }
        form = TehnickaDokumentacijaForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn("Poveznica mora biti unesena", str(form.errors))
