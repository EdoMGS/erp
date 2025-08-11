import os
import sys
from pathlib import Path

# ensure project root is on PYTHONPATH for Celery
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from celery import Celery

# set default Django settings module for celery program
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_root.settings.dev')

# initialize Celery app with Redis broker and backend
app = Celery(
    'project_root',
    broker=os.environ.get('REDIS_URL', 'redis://redis:6379/0'),
    backend=os.environ.get('REDIS_URL', 'redis://redis:6379/0'),
)
# configure Celery from Django settings, using 'CELERY_' namespace
app.config_from_object('django.conf:settings', namespace='CELERY')
# auto-discover tasks from installed apps
app.autodiscover_tasks()
