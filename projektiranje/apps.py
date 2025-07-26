# projektiranje/apps.py

from django.apps import AppConfig


class ProjektiranjeAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "projektiranje"
    verbose_name = "Projektiranje App"
