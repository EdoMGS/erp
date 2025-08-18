"""
conftest.py

Ensures project root is on sys.path early so absolute imports like 'tests.factories' work
under --import-mode=importlib. Also guarantees DJANGO_SETTINGS_MODULE is set before any
Django-dependent imports in factory modules.
"""
import os
import sys

root = os.path.abspath(os.path.dirname(__file__))
if root not in sys.path:
    sys.path.insert(0, root)
# Fallback environment variable if not already defined
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project_root.settings.test")
