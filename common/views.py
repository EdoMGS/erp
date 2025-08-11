from rest_framework import viewsets

from .models import ActiveManager, AuditTrail, BaseModel, Notification, Role
from .serializers import (
    ActiveManagerSerializer,
    AuditTrailSerializer,
    BaseModelSerializer,
    NotificationSerializer,
    RoleSerializer,
)


class ActiveManagerViewSet(viewsets.ModelViewSet):
    queryset = ActiveManager.objects.all()
    serializer_class = ActiveManagerSerializer


class BaseModelViewSet(viewsets.ModelViewSet):
    queryset = BaseModel.active_objects.all()
    serializer_class = BaseModelSerializer


class AuditTrailViewSet(viewsets.ModelViewSet):
    queryset = AuditTrail.objects.all()
    serializer_class = AuditTrailSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
