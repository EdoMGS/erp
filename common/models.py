# common/models.py

from decimal import Decimal

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class BaseModel(models.Model):
    """
    Abstract base model that should be used for all models in the project
    """

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        verbose_name=_("Created by"),
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        verbose_name=_("Updated by"),
    )

    objects = models.Manager()
    active_objects = ActiveManager()

    class Meta:
        abstract = True
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)


class FinancialTrackingMixin(models.Model):
    """Mixin for financial tracking across modules"""

    amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    financial_reference = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        abstract = True

    def get_financial_details(self):
        return self.financial_details if hasattr(self, "financial_details") else None

    def update_financial_status(self):
        if hasattr(self, "financial_details"):
            self.financial_details.recalculate()


class AuditableMixin(models.Model):
    """Mixin for audit logging"""

    last_modified = models.DateTimeField(auto_now=True)
    audit_notes = models.TextField(blank=True, null=True)

    class Meta:
        abstract = True

    def log_change(self, user, change_type, notes=None):
        from common.models import AuditLog

        AuditLog.objects.create(content_object=self, user=user, change_type=change_type, notes=notes)


class NotificationMixin(models.Model):
    """Mixin for notification functionality"""

    class Meta:
        abstract = True

    def send_notification(self, title, message, recipients=None):
        from common.utils import send_notification

        send_notification(
            title=title,
            message=message,
            object_type=self.__class__.__name__,
            object_id=self.id,
            recipients=recipients,
        )


class AuditTrail(models.Model):
    """
    Evidencija akcija. Referenciramo 'ljudski_resursi.Employee' preko stringa
    da izbjegnemo kružni import.
    """

    action = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        "ljudski_resursi.Employee",
        related_name="audittrail_user",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    audit_notes = models.TextField(null=True, blank=True)
    action_taken = models.CharField(max_length=200)

    # Primjer ako treba i "recipient"
    recipient = models.ForeignKey(
        "ljudski_resursi.Employee",
        related_name="audittrail_recipient",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"AuditTrail: {self.action} by {self.user}"


class Notification(models.Model):
    """
    Jednostavne notifikacije - referenciraju Employee
    """

    recipient = models.ForeignKey("ljudski_resursi.Employee", on_delete=models.CASCADE)
    message = models.TextField()
    enabled = models.BooleanField(default=True)
    notification_enabled = models.BooleanField(default=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification to {self.recipient} - {self.message}"


class Role(models.Model):
    """
    Ujedinjeni model Role (ako je bio dupliciran).
    """

    name = models.CharField(max_length=255, unique=True, verbose_name="Role Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    # permissions = models.JSONField(blank=True, null=True, verbose_name="Permissions") # po želji

    def __str__(self):
        return self.name
