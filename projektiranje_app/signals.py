import logging

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import BillOfMaterials, DesignSegment, DesignTask
from .services import NotificationService

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=DesignTask)
def design_task_pre_save(sender, instance, **kwargs):
    try:
        with transaction.atomic():
            if instance.status == 'done' and not instance.datum_zavrsetka:
                instance.zavrsi_dizajn()
    except ValidationError as e:
        logger.error(f"Validation error in design_task_pre_save: {str(e)}")
        raise

@receiver(post_save, sender=DesignTask)
def design_task_post_save(sender, instance, created, **kwargs):
    try:
        with transaction.atomic():
            if created:
                # Create initial BOM
                BillOfMaterials.objects.create(
                    design_task=instance,
                    naziv=f"Glavni BOM - {instance.projekt}",
                    status="draft"
                )

            # Send notifications
            NotificationService.notify_stakeholders(
                instance, 
                'design_task_update',
                f"Design task for {instance.projekt} status: {instance.status}"
            )
    except Exception as e:
        logger.error(f"Error in design_task_post_save: {str(e)}")
        raise

@receiver(post_save, sender=DesignSegment)
def design_segment_post_save(sender, instance, created, **kwargs):
    try:
        if created:
            NotificationService.notify_stakeholders(
                instance,
                'design_segment_created',
                f"New design segment created for {instance.design_task}"
            )
    except Exception as e:
        logger.error(f"Error in design_segment_post_save: {str(e)}")
        raise