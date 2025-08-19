import os
import django
import pytest

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_root.settings.test')
django.setup()


@pytest.fixture(scope="session", autouse=True)
def seed_minimal_accounts(django_db_setup, django_db_blocker):  # noqa: D401
    """Seed only the minimal accounts needed for ledger tests (120 receivable, 400 revenue)."""
    from financije.models import Account

    with django_db_blocker.unblock():
        # Map of account number -> (name, account_type)
        # Valid account_type choices: active, passive, income, expense
        needed = {
            "120": ("Kupci", "active"),
            "400": ("Prihodi usluge", "income"),
            "140": ("Zalihe", "active"),
            "150": ("WIP", "active"),
            "220": ("Dobavljači", "passive"),
            "500": ("COGS", "expense"),
            "699": ("Otpad / Razlike", "expense"),
        }

        for number, (name, atype) in needed.items():
            obj, created = Account.objects.get_or_create(
                number=number,
                defaults={"name": name, "account_type": atype},
            )
            if created:
                print(
                    f"[seed_minimal_accounts] Created account {number} {name} {atype}"
                )

        missing = [n for n in needed if not Account.objects.filter(number=n).exists()]
        assert not missing, f"Missing seeded accounts: {missing}"
