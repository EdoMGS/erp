import logging

from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask

from financije.services import process_completed_work_order

from .models import Proizvodnja, Projekt, RadniNalog

logger = logging.getLogger(__name__)


def create_or_update_periodic_task(name, task, schedule, **kwargs):
    """Helper function to create or update periodic tasks with unique names"""
    timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
    unique_name = f"{name}_{timestamp}"

    try:
        # Try to find existing task by base name
        existing_task = PeriodicTask.objects.filter(name__startswith=name + "_").first()

        if existing_task:
            # Update existing task
            existing_task.interval = schedule
            existing_task.enabled = True
            for key, value in kwargs.items():
                setattr(existing_task, key, value)
            existing_task.save()
            return existing_task
        else:
            # Create new task with unique name
            return PeriodicTask.objects.create(
                interval=schedule, name=unique_name, task=task, **kwargs
            )
    except Exception as e:
        logger.error(f"Error creating/updating periodic task: {str(e)}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
)
def update_proizvodnja_status():
    """Ažurira statuse svih aktivnih proizvodnji"""
    try:
        with transaction.atomic():
            active_proizvodnje = Proizvodnja.objects.filter(
                is_active=True, status__in=["planirano", "u_progresu"]
            )

            for proizvodnja in active_proizvodnje:
                proizvodnja.update_statistics()
                logger.info(f"Updated stats for Proizvodnja ID: {proizvodnja.id}")

    except Exception as e:
        logger.error(f"Error in update_proizvodnja_status: {str(e)}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
    retry_backoff=True,
)
def update_radni_nalog_status(self, radni_nalog_id):
    """Ažurira status radnog naloga i procesira povezane akcije"""
    try:
        with transaction.atomic():
            radni_nalog = RadniNalog.objects.select_related("projekt", "proizvodnja").get(
                id=radni_nalog_id
            )

            previous_status = radni_nalog.status
            radni_nalog.azuriraj_status()

            # Ako je nalog završen, procesiraj financije
            if radni_nalog.status == "ZAVRSENO" and previous_status != "ZAVRSENO":
                process_completed_work_order(radni_nalog)

            radni_nalog.save()
            logger.info(f"Updated RadniNalog {radni_nalog_id} status to {radni_nalog.status}")

    except ObjectDoesNotExist:
        logger.warning(f"RadniNalog {radni_nalog_id} not found")
    except Exception as e:
        logger.error(f"Error processing RadniNalog {radni_nalog_id}: {str(e)}")
        raise


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3},
    retry_backoff=True,
)
def check_project_deadlines():
    """Provjerava rokove projekata i ažurira statuse"""
    try:
        today = timezone.now().date()
        projects = Projekt.objects.filter(is_active=True, status__in=["OTVOREN", "U_TIJEKU"])

        for project in projects:
            if project.rok_za_isporuku and project.rok_za_isporuku < today:
                project.status = "PROBIJEN_ROK"
                project.save(update_fields=["status"])
                logger.warning(f"Project {project.id} deadline exceeded")

    except Exception as e:
        logger.error(f"Error in check_project_deadlines: {str(e)}")
        raise


# Update Celery Beat schedule in settings.py:
# CELERY_BEAT_SCHEDULE.update({
#     'update-proizvodnja-status': {
#         'task': 'proizvodnja.tasks.update_proizvodnja_status',
#         'schedule': 300.0,  # 5 minutes
#     },
#     'check-project-deadlines': {
#         'task': 'proizvodnja.tasks.check_project_deadlines',
#         'schedule': 3600.0,  # 1 hour
#     }
# })

# Example usage:
schedule, _ = IntervalSchedule.objects.get_or_create(
    every=1,
    period=IntervalSchedule.HOURS,
)

create_or_update_periodic_task(
    name="proizvodnja-status-check",
    task="proizvodnja.tasks.check_project_status",
    schedule=schedule,
    enabled=True,
)
