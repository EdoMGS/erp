from django.db import models

# Create your models here.


class Tenant(models.Model):
    name = models.CharField(max_length=255, unique=True)
    domain = models.CharField(max_length=255, unique=True)
    schema_name = models.CharField(max_length=63, unique=True)

    def __str__(self):
        return self.name


class Company(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name="companies")
    name = models.CharField(max_length=255)

    class Meta:
        verbose_name = "Company"
        verbose_name_plural = "Companies"

    def __str__(self):
        return self.name
