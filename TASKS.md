### TASK: sprint0_bootstrap_core
repo: EdoMGS/erp
base_branch: feature/sprint0-skeleton
new_branch: core-start

SHELL
1. git checkout -b core-start feature/sprint0-skeleton
2. rm -rf asset_management asset_tracker asset_usage benefits client compliance dashboard dokumenti erp_assets financije job_costing ljudski_resursi nabava prodaja proizvodnja project_costing projektiranje skladiste static templates locale management \
        project_root *.coverage .env.* tests that belong to removed apps        # keep core/ common/ tenants/ accounts/ .github/ docker/ etc.
3. find . -name "__pycache__" -exec rm -rf {} +
4. poetry install || pip install -r requirements.txt
FILES
# common/models/base.py  (new)
import uuid
from django.db import models
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey("tenants.Tenant", on_delete=models.CASCADE, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta: abstract = True
# tenants/models.py  – ensure Tenant extends BaseModel
# accounts/models.py – leave CustomUser as is, add tenant FK if missing
# tenants/middleware.py  (new)
from django.db import connection
from tenants.models import Tenant
class TenantMiddleware:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        host = request.get_host().split(":")[0]
        request.tenant = Tenant.objects.filter(subdomain=host).first()
        connection.tenant = request.tenant
        return self.get_response(request)
# settings/base.py – add 'tenants.middleware.TenantMiddleware' high in MIDDLEWARE
# core/routers.py  (new) – no-op router, placeholder for future per-tenant routing
# fixtures/initial_data.json  (new) – superuser, Holding & Operativa companies, minimal chart (10 konta)
# .github/workflows/ci.yml – lint (black --check, flake8), pytest, docker build
# Makefile – targets: up test lint shell
TESTS
- tests/test_tenant_switch.py → assert two tenants isolated
- tests/test_basemodel_fields.py → check UUID, timestamps, tenant FK
CI
- all tests, lint, docker build pass (badge shows “passing”)
GIT
git add .
git commit -m "Sprint 0: core skeleton, multi-tenant groundwork"
git push -u origin core-start
gh pr create --base main --head core-start --title "Sprint 0: core skeleton" --body "Implements S0-01…S0-07"

DONE when PR green-lights CI and merges without conflicts.
