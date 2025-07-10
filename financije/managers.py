from django.db import models
from django.utils import timezone

class OverheadManager(models.Manager):
    def current(self):
        """Get current month's overhead"""
        today = timezone.now()
        return self.filter(
            godina=today.year,
            mjesec=today.month
        ).first()
