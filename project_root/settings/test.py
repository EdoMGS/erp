# Test settings
from .base import *  # noqa

# Use in-memory SQLite database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
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

# Define a static secret key for tests
SECRET_KEY = 'test-secret-key'
