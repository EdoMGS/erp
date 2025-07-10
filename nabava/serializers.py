from rest_framework import serializers

from .models import PurchaseOrderLine  # Dodano
from .models import (Dobavljac, GrupaDobavljaca, Narudzbenica,
                     NarudzbenicaStavka, ProcurementPlan, ProcurementRequest,
                     PurchaseOrder)


class ProcurementPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcurementPlan
        fields = "__all__"


class ProcurementRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProcurementRequest
        fields = "__all__"


class PurchaseOrderSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source="supplier.naziv", read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            "id",
            "supplier",
            "supplier_name",
            "order_date",
            "expected_delivery_date",
            "status",
            "work_order",
            "is_jit",
            "delivery_schedule",
            "reference_price",
            "agreed_price",
            "justification_for_deviation",
        ]


class PurchaseOrderLineSerializer(serializers.ModelSerializer):
    artikl_naziv = serializers.CharField(source="artikl.naziv", read_only=True)

    class Meta:
        model = PurchaseOrderLine
        fields = [
            "id",
            "purchase_order",
            "artikl",
            "artikl_naziv",
            "quantity",
            "unit_price",
            "discount",
            "received_quantity",
        ]


class NarudzbenicaStavkaSerializer(serializers.ModelSerializer):
    class Meta:
        model = NarudzbenicaStavka
        fields = "__all__"


class NarudzbenicaSerializer(serializers.ModelSerializer):
    stavke = NarudzbenicaStavkaSerializer(many=True, read_only=True)

    class Meta:
        model = Narudzbenica
        fields = "__all__"


class DobavljacSerializer(serializers.ModelSerializer):
    grupa_naziv = serializers.CharField(source="grupa.naziv", read_only=True)

    class Meta:
        model = Dobavljac
        fields = "__all__"


class GrupaDobavljacaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupaDobavljaca
        fields = "__all__"
