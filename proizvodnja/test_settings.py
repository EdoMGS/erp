from django.conf import settings

def test_settings_module():
    assert settings.SECRET_KEY == 'django-insecure-your_secret_key_here'
