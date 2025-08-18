### TASK: bootstrap_min_sprint0
repo: EdoMGS/erp
base_branch: main
new_branch: sprint0-bootstrap

SHELL
1) git checkout -b sprint0-bootstrap main
2) python -m pip install -q django==4.2.23 pytest pytest-django black==24.4.2 isort==5.13.2 autoflake==2.3.1 pre-commit flake8

FILES
# requirements.txt
Django>=4.2,<5.0
pytest
pytest-django
black==24.4.2
isort==5.13.2
autoflake==2.3.1
flake8

# project_root/__init__.py
# empty

# manage.py
#!/usr/bin/env python
import os, sys
if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_root.settings.dev")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)

# project_root/settings/__init__.py
from .base import *

# project_root/settings/base.py
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent.parent
SECRET_KEY = "dev-only-change-me"
DEBUG = True
ALLOWED_HOSTS = ["*"]
INSTALLED_APPS = [
    "django.contrib.admin","django.contrib.auth","django.contrib.contenttypes",
    "django.contrib.sessions","django.contrib.messages","django.contrib.staticfiles",
    "common","tenants","core",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "project_root.urls"
TEMPLATES = [{
    "BACKEND":"django.template.backends.django.DjangoTemplates","DIRS":[],
    "APP_DIRS":True,"OPTIONS":{"context_processors":[
        "django.template.context_processors.debug","django.template.context_processors.request",
        "django.contrib.auth.context_processors.auth","django.contrib.messages.context_processors.messages"]}}]
WSGI_APPLICATION = "project_root.wsgi.application"
DATABASES = {"default":{"ENGINE":"django.db.backends.sqlite3","NAME": BASE_DIR/"db.sqlite3"}}
LANGUAGE_CODE="en-us"; TIME_ZONE="UTC"; USE_I18N=True; USE_TZ=True
STATIC_URL="static/"
DEFAULT_AUTO_FIELD="django.db.models.BigAutoField"

# project_root/settings/dev.py
from .base import *

# project_root/settings/test.py
from .base import *
SECRET_KEY = "dummy"
DATABASES = {"default":{"ENGINE":"django.db.backends.sqlite3","NAME":":memory:"}}
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
AUTH_PASSWORD_VALIDATORS = []

# project_root/urls.py
from django.contrib import admin
from django.urls import path
urlpatterns = [path("admin/", admin.site.urls)]

# project_root/wsgi.py
import os
from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_root.settings.dev")
application = get_wsgi_application()

# common/apps.py
from django.apps import AppConfig
class CommonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "common"

# common/models.py
# placeholder for BaseModel in next sprint

# tenants/apps.py
from django.apps import AppConfig
class TenantsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "tenants"

# tenants/models.py
from django.db import models
class Tenant(models.Model):
    name = models.CharField(max_length=120)
    subdomain = models.CharField(max_length=80, unique=True)
    def __str__(self): return self.name

# core/apps.py
from django.apps import AppConfig
class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = project_root.settings.test
python_files = test_*.py *_tests.py
addopts = -q

# tests/test_smoke.py
def test_imports():
    import project_root.settings.base  # noqa
    import tenants.models  # noqa

# .pre-commit-config.yaml  (ograničeno na nove mape)
repos:
  - repo: https://github.com/pycqa/autoflake
    rev: v2.3.1
    hooks:
      - id: autoflake
        args: [--remove-all-unused-imports, --remove-unused-variables]
        files: ^(common|tenants|core|project_root)/
  - repo: https://github.com/psf/black
    rev: 24.4.2
    hooks:
      - id: black
        files: ^(common|tenants|core|project_root)/
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ["--profile","black"]
        files: ^(common|tenants|core|project_root)/

# .github/workflows/ci.yml  (minimal, zelen)
name: Django CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11", cache: pip }
      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pre-commit
      - name: pre-commit
        run: pre-commit run --all-files
      - name: Lint/format (scoped)
        run: |
          black --check common tenants core project_root
          isort --check-only common tenants core project_root
          autoflake --check -r --remove-all-unused-imports --remove-unused-variables \
            common tenants core project_root
      - name: Pytest
        env:
          DJANGO_SETTINGS_MODULE: project_root.settings.test
          SECRET_KEY: dummy
        run: pytest

GIT
git add .
git commit -m "Sprint0: minimal Django skeleton + CI green"
git push -u origin sprint0-bootstrap
gh pr create --base main --head sprint0-bootstrap --title "Sprint 0: minimal skeleton" --body "Django 4.2 + common/tenants/core, pre-commit, CI, smoke test."
