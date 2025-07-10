from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class TimestampMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class FinancialMixin(models.Model):
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    def validate_positive_amount(self):
        if self.amount < 0:
            raise ValidationError("Amount cannot be negative")

    class Meta:
        abstract = True

class AuditableMixin(models.Model):
    """Base mixin for audit tracking"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_created',
    )
    updated_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_updated',
    )

    class Meta:
        abstract = True

class StatusTrackingMixin(models.Model):
    """Mixin for status tracking"""
    status_changed_at = models.DateTimeField(null=True)
    previous_status = models.CharField(max_length=50, blank=True)
    status_changed_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='%(class)s_status_changes'
    )

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if self.pk:
            old_instance = self.__class__.objects.get(pk=self.pk)
            if hasattr(self, 'status') and old_instance.status != self.status:
                self.previous_status = old_instance.status
                self.status_changed_at = timezone.now()
        super().save(*args, **kwargs)
