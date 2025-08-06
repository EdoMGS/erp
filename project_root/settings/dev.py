# Development settings for the Django project

import os

import environ

from .base import *

# Load .env.dev
env = environ.Env()
environ.Env.read_env(env_file='.env.dev')

# Celery Configuration: broker and result backend using Redis
# Use in-memory broker so no DNS lookup in dev
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'rpc://'  # or 'memory://' if preferred


# Database configuration (using SQLite for dev)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# If you prefer to connect to a local Postgres instead of SQLite, uncomment and configure:
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': os.environ.get('POSTGRES_DB', 'erp'),
#         'USER': os.environ.get('POSTGRES_USER', 'erp'),
#         'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'erp'),
#         'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
#         'PORT': os.environ.get('POSTGRES_PORT', '5432'),
#     }
# }

# Celery beat scheduler settings to reduce startup noise in dev
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers.DatabaseScheduler"
CELERY_BEAT_SYNC_EVERY = 600  # seconds, reduces startup queries
# Add your development-specific settings here
