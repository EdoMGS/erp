from django.conf import settings
from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=255, unique=True, verbose_name="Domain")

    def __str__(self):
        return self.name


class TenantUser(models.Model):
    ROLE_CHOICES = [
        ("owner", "Owner"),
        ("manager", "Manager"),
        ("staff", "Staff"),
    ]

    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    class Meta:
        unique_together = ("tenant", "user")

    def __str__(self):
        return f"{self.user} @ {self.tenant} ({self.role})"
