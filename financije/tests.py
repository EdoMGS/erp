from django.test import TestCase
from django.urls import reverse
from decimal import Decimal
from .models import Invoice, TaxConfiguration
from django.contrib.auth import get_user_model

class InvoiceTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        # ...existing setup code...

    def test_invoice_creation(self):
        # Add test implementation
        pass

    # ...existing test methods...

class TaxConfigurationTests(TestCase):
    def setUp(self):
        self.tax_config = TaxConfiguration.objects.create(
            name="Test Config",
            tax_rate=Decimal('25.00')
        )

    def test_tax_calculation(self):
        # Add test implementation
        pass

    # ...existing test methods...
