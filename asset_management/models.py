from django.db import models

# Create your models here.


class Asset(models.Model):
    name = models.CharField(max_length=255)
    purchase_date = models.DateField()
    value = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class AssetUsage(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    usage_date = models.DateField()
    usage_hours = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.asset.name} - {self.usage_date}"


class FixedCost(models.Model):
    name = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name


class VariableCostPreset(models.Model):
    name = models.CharField(max_length=255)
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.name
