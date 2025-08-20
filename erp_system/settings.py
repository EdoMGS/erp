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
    # Core / infra
    *INSTALLED_APPS,  # inherit base apps from imported base settings
    # Active domain apps (legacy moved to legacy_disabled and excluded)
    "financije",
    "prodaja",
    "inventory",
    "project_costing",
    "tenants",
    "ljudski_resursi",
]
