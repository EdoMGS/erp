from .base import *  # noqa: F403

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# Ensure all core Django apps are present for test
if "django.contrib.contenttypes" not in INSTALLED_APPS:
    INSTALLED_APPS = ["django.contrib.contenttypes"] + list(
        INSTALLED_APPS
    )  # noqa: F405
