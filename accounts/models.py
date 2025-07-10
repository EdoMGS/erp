# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUser(AbstractUser):
    """
    Minimalno prilagođeni User.
    Uklonili smo polje 'department' kako bismo izbjegli kružnu ovisnost
    (Employee -> CustomUser -> Department -> Employee).
    """
    email = models.EmailField(unique=True, verbose_name=_("Email Address"))
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='customuser_set',
        blank=True,
        help_text=_('The groups this user belongs to.'),
        verbose_name=_('groups'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='customuser_set',
        blank=True,
        help_text=_('Specific permissions for this user.'),
        verbose_name=_('user permissions'),
    )

    # Ako želiš role, mozes dodati many-to-many
    # roles = models.ManyToManyField('common.Role', blank=True, related_name='users')

    def __str__(self):
        return f"{self.username} ({self.email})"
