from django.core.validators import RegexValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from financije.models import Invoice  # Updated to import from financije
from prodaja.models import (SalesOpportunity,  # Updated to import from prodaja
                            SalesOrder)

from .models import ClientActivityLog, ClientSupplier


class ClientSupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientSupplier
        fields = [
            'id', 'name', 'email', 'phone', 'oib', 'address',
            'city', 'postal_code', 'county', 'country',
            'is_active', 'is_supplier', 'relationship_status',
            'long_term_relationship', 'date_created', 'date_updated'
        ]
        read_only_fields = ['date_created', 'date_updated']

class ClientActivityLogSerializer(serializers.ModelSerializer):
    client_name = serializers.CharField(source='client.name', read_only=True)

    class Meta:
        model = ClientActivityLog
        fields = ['id', 'client', 'client_name', 'activity', 'activity_type', 'timestamp']
        read_only_fields = ['timestamp']

class SalesOpportunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOpportunity
        fields = '__all__'

class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = '__all__'

class SalesOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SalesOrder
        fields = '__all__'