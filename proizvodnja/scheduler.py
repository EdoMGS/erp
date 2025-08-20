import logging

from django.utils import timezone
from django_celery_beat.models import IntervalSchedule, PeriodicTask

logger = logging.getLogger(__name__)


def initialize_scheduler():
    """Initialize or update periodic tasks"""
    try:
        schedule, _ = IntervalSchedule.objects.get_or_create(
            every=1,
            period=IntervalSchedule.HOURS,
        )

        timestamp = timezone.now().strftime("%Y%m%d_%H%M%S")
        task_name = f"check_project_status_{timestamp}"

        # Try to find existing task
        existing_task = PeriodicTask.objects.filter(
            task="proizvodnja.tasks.check_project_status"
        ).first()

        if existing_task:
            # Update existing task
            existing_task.interval = schedule
            existing_task.enabled = True
            existing_task.save()
            logger.info(f"Updated existing periodic task: {existing_task.name}")
        else:
            # Create new task with unique name
            PeriodicTask.objects.create(
                interval=schedule,
                name=task_name,
                task="proizvodnja.tasks.check_project_status",
                enabled=True,
            )
            logger.info(f"Created new periodic task: {task_name}")

    except Exception as e:
        logger.error(f"Error initializing scheduler: {str(e)}")
