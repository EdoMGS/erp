from decimal import Decimal

from django.conf import settings
from django.db import models

from tenants.models import Tenant


class Project(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    revenue = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0.00"))
    division = models.CharField(max_length=64)
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    def __str__(self):
        return self.name


class CostLine(models.Model):
    TYPE_CHOICES = [
        ("MAT", "Materijal"),
        ("ENE", "Energija"),
        ("OTH", "Ostalo"),
    ]
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="cost_lines")
    type = models.CharField(max_length=8, choices=TYPE_CHOICES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)


class LabourEntry(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="labour_entries")
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    date = models.DateField()
    worker_name = models.CharField(max_length=255)
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2)
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.worker_name} - {self.project.name}"


class MaterialUsage(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    material_name = models.CharField(max_length=255)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.material_name} - {self.project.name}"


class ProfitShareConfig(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="profit_share_config")
    owner_share = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("20.00"))
    worker_share = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("30.00"))
    company_share = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal("50.00"))


class WorkerShare(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="worker_shares")
    worker = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
