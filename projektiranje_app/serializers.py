from rest_framework import serializers

from .models import DesignTask


class DesignTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = DesignTask
        fields = ["id", "placeholder"]
