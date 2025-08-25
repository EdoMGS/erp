import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from financije.models.audit import AuditLog


@pytest.mark.django_db
def test_audit_log_is_immutable():
    User = get_user_model()
    user = User.objects.create(username="u")
    log = AuditLog.objects.create(user=user, action="a", model_name="M", instance_id=1)

    # update should raise
    with pytest.raises(ValidationError):
        log.action = "b"
        log.save()

    # deletion should raise
    with pytest.raises(ValidationError):
        log.delete()
