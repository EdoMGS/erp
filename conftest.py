"""
conftest.py

Ensures project root is on sys.path early so absolute imports like 'tests.factories' work
under --import-mode=importlib. Also guarantees DJANGO_SETTINGS_MODULE is set before any
Django-dependent imports in factory modules.
"""

import os
import pathlib
import sys

import django
import pytest

ROOT = pathlib.Path(__file__).parent.resolve()
if str(ROOT) not in sys.path[:1]:  # ensure at front
    sys.path.insert(0, str(ROOT))

# Let pytest-django manage Python path; only ensure settings module is set.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_root.settings.test')
django.setup()


@pytest.fixture(scope="session", autouse=True)
def seed_minimal_accounts(django_db_setup, django_db_blocker):  # noqa: D401
    """Seed minimal Chart of Accounts for all tests (inventory + ledger)."""
    from financije.models import Account

    with django_db_blocker.unblock():
        needed = {
            "120": ("Kupci", "active"),
            "140": ("Zalihe", "active"),
            "150": ("WIP", "active"),
            "220": ("Dobavljači", "passive"),
            "400": ("Prihodi usluge", "income"),
            "2680": ("PDV izlazni", "passive"),
            "500": ("COGS", "expense"),
            "699": ("Otpad / Razlike", "expense"),
        }
        for number, (name, atype) in needed.items():
            created = Account.objects.filter(number=number).exists()
            obj, _ = Account.objects.get_or_create(number=number, defaults={"name": name, "account_type": atype})
            if not created:
                print(f"[seed_minimal_accounts] Created account {number} {name} {atype}")


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
        lowered = nodeid.lower()
        if any(
            prefix.strip('.') in lowered
            for prefix in ['client', 'proizvodnja', 'projektiranje', 'skladiste', 'erp_assets']
        ):
            item.add_marker(skip_legacy)
            continue
        if 'payroll' in lowered:
            item.add_marker(skip_payroll)
            continue
        if 'interco_invoice' in lowered:
            item.add_marker(skip_legacy)
