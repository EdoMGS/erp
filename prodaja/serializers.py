from decimal import Decimal

from django.conf import settings
from rest_framework import serializers

from .models import Offer


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = Offer
        fields = [
            'id', 'customer', 'service_lines', 'material_lines',
            'total_amount', 'status', 'created_at', 'updated_at'
        ]
        read_only_fields = ['total_amount', 'created_at', 'updated_at']

    def _calculate_total(self, data_list, rate_map):
        total = Decimal('0.00')
        for item in data_list:
            key = item.get('key')
            qty = Decimal(item.get('quantity', 1))
            rate = rate_map.get(key, Decimal('0.00'))
            total += rate * qty
        return total

    def create(self, validated_data):
        service_lines = validated_data.pop('service_lines', [])
        material_lines = validated_data.pop('material_lines', [])
        total = self._calculate_total(service_lines, settings.SERVICE_RATES)
        total += self._calculate_total(material_lines, settings.MATERIAL_RATES)
        validated_data['total_amount'] = total
        validated_data['service_lines'] = service_lines
        validated_data['material_lines'] = material_lines
        return super().create(validated_data)

    def update(self, instance, validated_data):
        service_lines = validated_data.get('service_lines', instance.service_lines)
        material_lines = validated_data.get('material_lines', instance.material_lines)
        total = self._calculate_total(service_lines, settings.SERVICE_RATES)
        total += self._calculate_total(material_lines, settings.MATERIAL_RATES)
        validated_data['total_amount'] = total
        return super().update(instance, validated_data)
