# Import base settings (INSTALLED_APPS, middleware, etc.)
from .base import *  # noqa: F401,F403

# Override DB: Use file-based SQLite for tests to avoid multi-connection in-memory table loss
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'test_db.sqlite3',
    }
}

# Disable password validation for testing
AUTH_PASSWORD_VALIDATORS = []

# Use a faster password hasher for testing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Other test-specific settings can go here

# No INSTALLED_APPS override; using base INSTALLED_APPS for tests
# Add any test-specific apps here if needed

CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'rpc://'
