import pytest

pytestmark = pytest.mark.skip(reason="Legacy client_app smoke test disabled")


def test_placeholder_client():
    assert True
