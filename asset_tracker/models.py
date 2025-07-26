from django.db import models

# Create your models here.


class Asset(models.Model):
    type = models.CharField(max_length=100)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    owner_tenant = models.CharField(max_length=100)
    hour_rate = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.type} ({self.owner_tenant})"


class AssetUsage(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    project = models.CharField(max_length=100)
    km_or_hours = models.DecimalField(max_digits=8, decimal_places=2)
    amount = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Usage of {self.asset} for {self.project}"
