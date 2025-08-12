# proizvodnja/apps.py
import logging

from django.apps import AppConfig, apps
from django.db import connections
from django.db.utils import OperationalError

logger = logging.getLogger(__name__)


class ProizvodnjaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "proizvodnja"

    def ready(self):
        if not apps.is_installed("django_celery_beat"):
            return

        try:
            connection = connections["default"]
            if "django_celery_beat_periodictask" in connection.introspection.table_names():
                from .scheduler import initialize_scheduler

                initialize_scheduler()
        except OperationalError:
            logger.warning("Celery beat tables missing; skipping scheduler init.")
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {str(e)}")
