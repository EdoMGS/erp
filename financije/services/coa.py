"""Helpers for loading the minimal Croatian chart of accounts."""

from financije.models import Account

COA_HR_MIN = [
    ("110", "Bank account", "active"),
    ("120", "Accounts receivable", "active"),
    ("220", "Accounts payable", "passive"),
    ("270", "Advances received", "passive"),
    ("400", "Sales revenue", "income"),
    ("470", "VAT payable", "passive"),
    ("471", "VAT receivable", "active"),
    ("500", "Expense", "expense"),
    ("2600", "Profit share - company", "passive"),
    ("2601", "Profit share - workers", "passive"),
    ("7600", "Profit share expense", "expense"),
    ("8400", "Profit share - owner", "passive"),
    ("4999", "Rounding difference", "income"),
]


def load_coa_hr_min(tenant) -> list[Account]:
    """Load a minimal HR chart of accounts for ``tenant``.

    The loader is idempotent – running it multiple times will not create
    duplicate accounts. A list of ``Account`` instances present after the load is
    returned for convenience.
    """

    accounts: list[Account] = []
    for number, name, acc_type in COA_HR_MIN:
        acct, _ = Account.objects.get_or_create(
            tenant=tenant,
            number=number,
            defaults={"name": name, "account_type": acc_type},
        )
        accounts.append(acct)
    return accounts


__all__ = ["load_coa_hr_min"]
