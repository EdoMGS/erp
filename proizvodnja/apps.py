# proizvodnja/apps.py
from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class ProizvodnjaConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "proizvodnja"

    def ready(self):
        try:
            from .scheduler import initialize_scheduler
            initialize_scheduler()
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {str(e)}")
