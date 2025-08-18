from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    # Allow null/blank so tests creating multiple tenants without domain don't violate unique constraint
    domain = models.CharField(max_length=255, unique=True, null=True, blank=True, verbose_name="Domain")

    def __str__(self):
        return self.name
