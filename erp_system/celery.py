import os

from celery import Celery

# 1. Koje postavke Django koristi
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "erp_system.settings.dev")  # ili prod.py kad dođe vrijeme

# 2. Instanciraj Celery
app = Celery("erp_system")

# 3. Učitaj konfiguraciju iz Django settings (prefiks CELERY_)
app.config_from_object("django.conf:settings", namespace="CELERY")

# 4. Sam pronađi tasks u svim INSTALLED_APPS
app.autodiscover_tasks()

# <--- nova linija
app.conf.broker_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
