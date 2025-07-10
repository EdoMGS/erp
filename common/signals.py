import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils import timezone

from common.utils import send_notification
from financije.models import FinancialDetails
from proizvodnja.models import RadniNalog
from skladiste.models import Artikl

from .models import Notifikacija

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Notifikacija)
def send_notification(sender, instance, created, **kwargs):
    if created:
        channel_layer = get_channel_layer()
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    f"notifikacije_{instance.korisnik.id}",
                    {"type": "send_notification", "message": instance.poruka}
                )
            except Exception as e:
                logger.error(f"Failed to send notification: {e}")

@receiver(post_save, sender=RadniNalog)
def handle_work_order_updates(sender, instance, created, **kwargs):
    """Central handler for work order changes"""
    try:
        # Update inventory
        Artikl.objects.filter(radni_nalog=instance).update(
            status='reserved' if instance.status == 'U_TIJEKU' else 'available'
        )
        
        # Update financial tracking
        FinancialDetails.objects.update_or_create(
            related_work_order=instance,
            defaults={'predicted_costs': instance.calculate_predicted_costs()}
        )
        
        # Notify relevant users
        send_notification(
            title="Work Order Update",
            message=f"Work order {instance.broj_naloga} status: {instance.status}",
            recipients=[instance.zaduzena_osoba, instance.created_by]
        )
    except Exception as e:
        logger.error(f"Error in handle_work_order_updates: {e}")