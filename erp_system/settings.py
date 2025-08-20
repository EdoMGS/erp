import os  # noqa: F401

from config.settings.base import *  # noqa: F403

# Load environment-specific settings
ENVIRONMENT = os.getenv("DJANGO_ENV", "base")
if ENVIRONMENT == "dev":
    from config.settings.dev import *  # noqa: F403
elif ENVIRONMENT == "prod":
    from config.settings.prod import *  # noqa: F403

AUTH_USER_MODEL = "users.CustomUser"

MIDDLEWARE += ["core.middleware.tenant_middleware.TenantMiddleware"]  # noqa: F405

INSTALLED_APPS = [
    # Core / infra
    *INSTALLED_APPS,  # inherit base apps from imported base settings  # noqa: F405
    # Active domain apps (legacy moved to legacy_disabled and excluded)
    "financije",
    "prodaja",
    "inventory",
    "project_costing",
    "tenants",
    "ljudski_resursi",
    # erp_assets quarantined -> legacy_disabled/erp_assets
]
