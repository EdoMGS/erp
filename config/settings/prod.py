# Production settings


DEBUG = False

ALLOWED_HOSTS = ["your-production-domain.com"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "erp_prod",
        "USER": "postgres",
        "PASSWORD": "secure-password",
        "HOST": "db-server",
        "PORT": "5432",
    }
}

SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
