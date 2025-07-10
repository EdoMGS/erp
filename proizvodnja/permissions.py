# proizvodnja/permissions.py
from rest_framework import permissions
from django.conf import settings
from ljudski_resursi.models import Employee

class BaseProizvodnjaPermission(permissions.BasePermission):
    """Base permission class for Proizvodnja app"""
    
    def has_employee_profile(self, user):
        return hasattr(user, 'employee') and isinstance(user.employee, Employee)
    
    def check_group_permission(self, user, group_name):
        return user.groups.filter(name=group_name).exists()

class ProizvodnjaPermission(BaseProizvodnjaPermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Allow read operations for employees
        if request.method in permissions.SAFE_METHODS:
            return self.has_employee_profile(request.user)
            
        # Check specific group permissions from settings
        required_groups = getattr(settings, 'PROIZVODNJA_EDIT_GROUPS', ['Proizvodnja'])
        return any(self.check_group_permission(request.user, group) 
                  for group in required_groups)

class IsRadniNalogOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.zaduzena_osoba == request.user

class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)

# Remove individual role permissions and use group-based approach
# This aligns better with Django's built-in group permissions
