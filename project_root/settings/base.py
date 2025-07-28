# Base settings for the Django project
from decimal import Decimal

INSTALLED_APPS = [
    # Django contrib apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Third-party apps
    'django_celery_beat',
    'django_celery_results',
    'import_export',

    # Project apps
    'tenants',
    'accounts',
    'asset_management',
    'asset_tracker',
    'asset_usage',
    'benefits',
    'client',
    'common',
    'compliance',
    'config',
    'core',
    'dashboard',
    'erp_assets',
    'financije',
    'job_costing',
    'ljudski_resursi',
    'nabava',
    'prodaja',
    'proizvodnja',
    'project_costing',
    'projektiranje',
    'skladiste',
]

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
