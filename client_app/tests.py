from django.test import TestCase
from .models import ClientSupplier
from rest_framework.test import APIClient
from rest_framework import status

class ClientSupplierTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            'name': 'Test Client',
            'address': '123 Test St',
            'email': 'test@example.com',
            'phone': '1234567890',
            'oib': '12345678901',
            # ...other fields...
        }
        self.invalid_payload = {
            'name': '',
            'address': '',
            'email': 'invalid_email',
            'phone': '123',
            'oib': 'abc',
            # ...other fields...
        }

    def test_create_valid_client(self):
        response = self.client.post('/clientsuppliers/', data=self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_invalid_client(self):
        response = self.client.post('/clientsuppliers/', data=self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ...additional tests...
