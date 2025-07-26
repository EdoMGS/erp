from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.core.mail import send_mail
from django.db import transaction

from common.events import EventManager


class NotificationService:
    @staticmethod
    def send_notification(user_id, message, notification_type="info"):
        """Send real-time notification"""
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user_id}_notifications",
            {
                "type": "notification.message",
                "message": message,
                "notification_type": notification_type,
            },
        )


class EmailService:
    @staticmethod
    def send_email_notification(subject, message, recipient_list):
        """Send email notification"""
        return send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )


class ModuleCommunicationService:
    @staticmethod
    @transaction.atomic
    def update_related_modules(source_module: str, action: str, data: dict):
        """Coordinate updates across multiple modules"""
        EventManager.notify_modules("module_update", {"source": source_module, "action": action, "data": data})


class FinancialTrackingService:
    @staticmethod
    def calculate_project_finances(project_id: int) -> dict:
        """Calculate financial metrics for a project"""
        from proizvodnja.models import Projekt

        project = Projekt.objects.get(id=project_id)
        return {
            "total_costs": project.calculate_actual_costs(),
            "predicted_profit": project.financial_details.predicted_profit,
        }
