from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import PurchaseOrder


@receiver(post_save, sender=PurchaseOrder)
def notify_on_purchase_order_status_change(sender, instance, created, **kwargs):
    if not created and instance.status == "sent":
        # Notify relevant parties
        subject = f"Narudžba {instance.id} poslana dobavljaču"
        message = f"Narudžba za {instance.supplier} je poslana."
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [instance.supplier.email],
            fail_silently=True,
        )
