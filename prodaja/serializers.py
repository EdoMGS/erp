from __future__ import annotations

from rest_framework import serializers


class ItemInputSerializer(serializers.Serializer):
    type = serializers.CharField()
    uom_base = serializers.CharField()
    qty_base = serializers.FloatField()
    area_m2 = serializers.FloatField(required=False, default=0.0)
    weight_kg = serializers.FloatField(required=False, default=0.0)
    paint_system_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    conditions = serializers.DictField(child=serializers.CharField(), required=False)


class QuoteInputSerializer(serializers.Serializer):
    tenant = serializers.CharField()
    currency = serializers.CharField()
    vat_rate = serializers.DecimalField(max_digits=6, decimal_places=2)
    is_vat_registered = serializers.BooleanField()
    risk_band = serializers.CharField()
    contingency_pct = serializers.DecimalField(max_digits=5, decimal_places=2)
    margin_target_pct = serializers.DecimalField(max_digits=5, decimal_places=2)
    items = ItemInputSerializer(many=True)
    options = serializers.ListField(child=serializers.CharField())
