from rest_framework import serializers

from .models import ActiveManager, AuditTrail, BaseModel, Notification, Role

# ...existing code...


class ActiveManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActiveManager
        fields = "__all__"


class BaseModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseModel
        fields = "__all__"


class AuditTrailSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditTrail
        fields = "__all__"


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = "__all__"


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = "__all__"
