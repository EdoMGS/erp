import os

from django.apps import AppConfig


class ClientAppConfig(AppConfig):
    # App module path is 'client', but we keep label 'client_app' to satisfy old migrations
    name = "client"
    label = "client_app"
    path = os.path.dirname(os.path.abspath(__file__))
    default_auto_field = "django.db.models.BigAutoField"
