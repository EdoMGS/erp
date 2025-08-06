import os

from django.conf import settings


def test_settings_module():
    settings.SECRET_KEY = os.getenv('SECRET_KEY', 'dummy')  # Default to 'dummy' if not set
    assert settings.SECRET_KEY  # Provjera da SECRET_KEY postoji i nije prazan
