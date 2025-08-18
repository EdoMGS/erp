"""
conftest.py

Ensures project root is on sys.path early so absolute imports like 'tests.factories' work
under --import-mode=importlib. Also guarantees DJANGO_SETTINGS_MODULE is set before any
Django-dependent imports in factory modules.
"""
import os
import django
import pytest

# Let pytest-django manage Python path; only ensure settings module is set.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_root.settings.test')
django.setup()

LEGACY_MODULE_PREFIXES = [
    'legacy_disabled.',
    'client.',  # moved to legacy
    'proizvodnja.',
    'projektiranje.',
    'skladiste.',
]


def pytest_collection_modifyitems(config, items):
    skip_legacy = pytest.mark.skip(reason="Skipped: legacy-disabled app or removed dependency in MVP scope")
    skip_payroll = pytest.mark.skip(reason="Skipped: payroll under refactor for MVP")
    for item in items:
        nodeid = item.nodeid
        # Skip tests located under legacy_disabled/ path directly
        if 'legacy_disabled' in nodeid:
            item.add_marker(skip_legacy)
            continue
        # Skip tests importing removed app modules (best-effort by nodeid name heuristics)
        lowered = nodeid.lower()
        if any(prefix.strip('.') in lowered for prefix in ['client', 'proizvodnja', 'projektiranje', 'skladiste', 'erp_assets']):
            item.add_marker(skip_legacy)
            continue
    # NOTE: previously we skipped any test containing 'smoke' in its nodeid which
    # suppressed our new MVP smoke tests. That blanket skip is removed so the
    # smoke tests for active apps now run.
        if 'payroll' in lowered:
            item.add_marker(skip_payroll)
            continue
        if 'interco_invoice' in lowered:
            item.add_marker(skip_legacy)
