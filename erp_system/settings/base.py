import os
from pathlib import Path

import environ

env = environ.Env(DEBUG=(bool, False))

BASE_DIR = Path(__file__).resolve().parent.parent.parent
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

# --- Core runtime flags with safe fallbacks for CI/local ephemeral environments ---
# We intentionally avoid passing a 'default=' kwarg into env() because the current
# type stubs in our toolchain flag it. Instead we perform manual fallbacks first.
_raw_debug = os.getenv("DEBUG")
if _raw_debug is None:
    DEBUG = True  # default to debug enabled for local / CI without explicit config
else:
    DEBUG = _raw_debug.lower() in {"1", "true", "yes", "on"}

# Provide a fallback SECRET_KEY for CI / ephemeral environments where env vars are not injected.
# This key MUST be overridden in any real deployment (production/staging).  # nosec
SECRET_KEY = os.getenv("SECRET_KEY") or "dev-insecure-placeholder-key"  # nosec

_raw_hosts = os.getenv("DJANGO_ALLOWED_HOSTS", "*")
ALLOWED_HOSTS = [h.strip() for h in _raw_hosts.split(",") if h.strip()]
if not ALLOWED_HOSTS:
    # Fallback wildcard so test/CI environment doesn't error on host header.
    ALLOWED_HOSTS = ["*"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # your domain apps go here
    "accounts",
    "client_app",
    "common",
    # multi-tenant support app (needed by financije and others)
    "tenants",
    "financije",
    # legacy apps moved under legacy_disabled
    # "nabava",
    "proizvodnja",  # stub reintroduced to satisfy historical migrations
    # removed obsolete stub projektiranje_app (replaced by projektiranje)
    "ljudski_resursi",
    "skladiste",  # stub reintroduced to satisfy historical migrations
    "prodaja",
    "django_celery_beat",
    "django_celery_results",
]

CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "erp_system.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

WSGI_APPLICATION = "erp_system.wsgi.application"

_raw_db_url = os.getenv("DATABASE_URL")
if _raw_db_url:
    # Use explicitly provided DATABASE_URL (e.g. Postgres in docker-compose)
    DATABASES = {"default": env.db()}
else:
    # Developer fallback: local sqlite so generic management commands work without running Postgres
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# Celery
CELERY_BROKER_URL = env("REDIS_URL")  # redis://redis:6379/0
CELERY_RESULT_BACKEND = env("REDIS_URL")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "hr"
TIME_ZONE = "Europe/Zagreb"
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Global default primary key type (silence warnings & ensure consistency)
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
