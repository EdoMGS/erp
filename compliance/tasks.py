from celery import shared_task
from django.core.mail import send_mail
from django.utils.timezone import now

from .models import ComplianceDocument


@shared_task
def send_expiry_reminders():
    today = now().date()
    expiring_soon = ComplianceDocument.objects.filter(expiry_date__lte=today)

    for document in expiring_soon:
        send_mail(
            subject=f"Expiry Reminder: {document.name}",
            message=f"The document '{document.name}' ({document.document_type}) is expiring on {document.expiry_date}.",
            from_email="noreply@erp-system.com",
            recipient_list=["admin@erp-system.com"],
        )
