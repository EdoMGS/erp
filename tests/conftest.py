import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_root.settings.test')
django.setup()
