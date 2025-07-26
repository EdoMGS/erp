from django.test import TestCase

from financije.models.others import FinancialDetails
from proizvodnja.models import Projekt


# Zadaci model ne postoji, pa je test uklonjen ili treba prilagoditi
class ProjektModelTest(TestCase):
    def test_projekt_creation(self):
        # Minimalni potrebni podaci za kreiranje Projekta
        financial_details = FinancialDetails.objects.create()
        projekt = Projekt.objects.create(naziv_projekta="Test Projekt", financial_details=financial_details)
        self.assertEqual(projekt.naziv_projekta, "Test Projekt")
