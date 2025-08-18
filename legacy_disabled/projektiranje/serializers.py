from rest_framework import serializers

from .models import (BillOfMaterials, BOMItem, CADDocument, DesignRevision,
                     DesignSegment, DesignTask, DynamicPlan)


class DesignTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignTask
        fields = "__all__"


class DesignSegmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignSegment
        fields = "__all__"


class DynamicPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicPlan
        fields = "__all__"


class BillOfMaterialsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillOfMaterials
        fields = "__all__"


class BOMItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = BOMItem
        fields = "__all__"


class CADDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CADDocument
        fields = "__all__"


class DesignRevisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignRevision
        fields = "__all__"
