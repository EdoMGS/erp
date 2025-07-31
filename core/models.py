from django.conf import settings
from django.db import models


class BaseModel(models.Model):
    """Abstract base model with audit fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
    )

    class Meta:
        abstract = True


class Company(BaseModel):
    name = models.CharField(max_length=255, unique=True)
    oib = models.CharField(max_length=25, blank=True, null=True)
    vat_id = models.CharField(max_length=50, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    currency = models.CharField(max_length=3)
    founded_at = models.DateField(null=True, blank=True)
    active = models.BooleanField(default=True)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="companies",
        blank=True,
    )

    def __str__(self):
        return self.name


class AppSetting(BaseModel):
    key = models.CharField(max_length=255)
    value = models.CharField(max_length=255)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="settings"
    )

    class Meta:
        unique_together = ("key", "company")

    def __str__(self):
        return f"{self.key} ({self.company})"
