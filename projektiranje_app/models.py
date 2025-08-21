"""Minimal stub models for projektiranje_app.

All legacy domain logic removed; only the DesignTask placeholder model
remains so historical foreign keys from other apps resolve.
"""

from django.db import models


class DesignTask(models.Model):
    placeholder = models.CharField(max_length=1, default="X")

    class Meta:
        verbose_name = "Design task (stub)"
        verbose_name_plural = "Design tasks (stub)"

    def __str__(self):
        return f"DesignTask {self.pk}"  # minimal readable repr
