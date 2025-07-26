import os

from config.settings.base import *

# Load environment-specific settings
ENVIRONMENT = os.getenv("DJANGO_ENV", "base")
if ENVIRONMENT == "dev":
    from config.settings.dev import *
elif ENVIRONMENT == "prod":
    from config.settings.prod import *

AUTH_USER_MODEL = "users.CustomUser"

MIDDLEWARE += ["core.middleware.tenant_middleware.TenantMiddleware"]

INSTALLED_APPS = [
    # ...existing apps...
    "client",
    "projektiranje",
    # ...existing apps...
]
