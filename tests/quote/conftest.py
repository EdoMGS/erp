import pytest


@pytest.fixture(scope="session", autouse=True)
def seed_minimal_accounts():
    """Override project fixture that requires database."""
    return
