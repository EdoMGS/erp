from django.conf import settings


def test_settings_module():
    assert settings.SECRET_KEY  # Provjera da SECRET_KEY postoji i nije prazan
