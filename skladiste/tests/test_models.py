"""Legacy skladiste tests intentionally skipped.

These tests referenced a fully featured legacy app that has been replaced by
lightweight stubs solely to satisfy historical migration dependencies. The
original model surface (Lokacija, Izdatnica, etc.) no longer exists in active
runtime; keeping the verbose legacy tests produces syntax / import errors and
adds no value. We retain this file (instead of deleting) to document the
intentional skip and avoid re‑introducing failing legacy assumptions.
"""

import pytest

pytestmark = pytest.mark.skip(reason="Legacy skladiste app replaced by stubs; tests disabled")


def test_placeholder():  # pragma: no cover - ensures test collector finds a test
    """Placeholder so pytest collection remains stable if skip mark removed accidentally."""
    assert True
