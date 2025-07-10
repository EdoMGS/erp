from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

from .models import Employee


class EmployeeAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                # Verify if user has an associated employee profile
                try:
                    employee = Employee.objects.get(user=user)
                    return user
                except Employee.DoesNotExist:
                    return None
            return None
        except User.DoesNotExist:
            return None
