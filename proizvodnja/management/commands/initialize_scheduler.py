import logging

from django.core.management.base import BaseCommand

from proizvodnja.scheduler import initialize_scheduler

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Initialize or update periodic tasks for the scheduler."

    def handle(self, *args, **kwargs):
        try:
            initialize_scheduler()
            self.stdout.write(self.style.SUCCESS("Scheduler initialized successfully."))
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {str(e)}")
            self.stderr.write(self.style.ERROR("Failed to initialize scheduler."))
