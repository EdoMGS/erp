import os

from django.apps import AppConfig


class ClientAppConfig(AppConfig):
    name = 'client_app'
    path = os.path.dirname(os.path.abspath(__file__))
    default_auto_field = 'django.db.models.BigAutoField'
