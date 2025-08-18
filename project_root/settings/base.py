# Base settings for the Django project
from decimal import Decimal
import os

INSTALLED_APPS = [
    # Django contrib apps
    # 'django.contrib.admin',  # Temporarily disabled to allow clean migration reset
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party minimal set
    'django_celery_beat',
    'django_celery_results',
    'import_export',
    # MVP project apps only
    'tenants',
    'accounts',
    'common',
    'core',
    'ljudski_resursi',
    'prodaja',
    'project_costing',
    'financije',  # temporary include
]

# Legacy apps moved out of scope for MVP are placed under legacy_disabled/ directory and removed from INSTALLED_APPS.

# Middleware configuration
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# Template configuration
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

"""
FIXTURE SETTINGS
"""
from pathlib import Path

# Base directory (directory containing manage.py)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Provide a default insecure secret for dev/test so tests don't fail when env var absent
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-placeholder-change-me")
# Look for fixtures in the repo-level fixtures/ directory
FIXTURE_DIRS = [BASE_DIR / 'fixtures']

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'accounts.CustomUser'

# Business rates configuration
SERVICE_RATES = {
    # 'service_key': Decimal('100.00'),
}

MATERIAL_RATES = {
    # 'material_key': Decimal('50.00'),
}

PROFIT_SHARE_CONFIG = {
    'dynamic_floor_pct': Decimal('0.10'),
    'floor_cap_per_month': Decimal('2000.00'),
}

MINIMAL_WAGE_CONFIG = {
    'gross_minimal': Decimal('951.72'),
    'net_minimal': Decimal('750.00'),
    'employer_contrib_pct': Decimal('16.5'),
    'meal_allowance_monthly': Decimal('100.00'),
    'housing_allowance_monthly': Decimal('600.00'),
}

# Provide a deterministic SECRET_KEY for non-production if none is set (tests/dev)
SECRET_KEY = os.environ.get('SECRET_KEY', 'test-secret-key')
