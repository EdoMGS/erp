# Development settings for the Django project

from .base import *
import os
import environ

# Load .env.dev
env = environ.Env()
environ.Env.read_env(env_file='.env.dev')

# Celery Configuration: broker and result backend using Redis
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://redis:6379/0')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://redis:6379/0')

# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'erp'),
        'USER': os.environ.get('POSTGRES_USER', 'erp'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'erp'),
        'HOST': os.environ.get('POSTGRES_HOST', 'db'),
        'PORT': os.environ.get('POSTGRES_PORT', '5432'),
    }
}

# Add your development-specific settings here
