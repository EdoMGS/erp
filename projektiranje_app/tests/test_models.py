from django.test import TestCase
from ..models import Projekt, Zadaci

class ProjektModelTest(TestCase):
    def test_projekt_creation(self):
        projekt = Projekt.objects.create(naziv="Test Projekt", datum_pocetka="2024-10-10")
        self.assertEqual(projekt.naziv, "Test Projekt")

class ZadaciModelTest(TestCase):
    def test_zadaci_creation(self):
        projekt = Projekt.objects.create(naziv="Test Projekt", datum_pocetka="2024-10-10")
        zadatak = Zadaci.objects.create(projekt=projekt, naziv="Test Zadatak", status="u tijeku")
        self.assertEqual(zadatak.naziv, "Test Zadatak")
