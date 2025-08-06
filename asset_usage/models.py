from django.db import models

from client.models import ClientSupplier


class AssetUsage(models.Model):
    client = models.ForeignKey(
        ClientSupplier,
        on_delete=models.CASCADE,
        related_name='asset_usages',
        verbose_name='Client for asset usage',
    )
    usage_date = models.DateField(verbose_name='Usage date')
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Usage amount',
    )
    invoiceable = models.BooleanField(
        default=True,
        verbose_name='Ready for invoicing',
    )
    is_deleted = models.BooleanField(
        default=False,
        verbose_name='Soft delete flag',
    )

    def __str__(self):
        return f"AssetUsage {self.pk} for {self.client}"
