from rest_framework import serializers

from .models import (Department, Employee, ExpertiseLevel, HierarchicalLevel,
                     Position)


class PositionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Position
        fields = "__all__"


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class ExpertiseLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpertiseLevel
        fields = "__all__"


class HierarchicalLevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = HierarchicalLevel
        fields = "__all__"


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = "__all__"
        extra_kwargs = {"expertise_level": {"source": "get_expertise_level_display"}}
