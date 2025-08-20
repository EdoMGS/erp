from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.timezone import now


class SoftDeleteModel(models.Model):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def delete(self, using=None, keep_parents=False):
        self.is_deleted = True
        self.deleted_at = now()
        self.save()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save()

    class Meta:
        abstract = True


class Asset(SoftDeleteModel):
    TYPE_CHOICES = [
        ("room", "Komora"),
        ("vehicle", "Vozilo"),
        ("hall", "Hala"),
    ]
    DIVISION_CHOICES = [
        ("BRAVARIJA", "Bravarija"),
        ("FARBANJE", "Farbanje"),
    ]
    type = models.CharField(max_length=32, choices=TYPE_CHOICES)
    value = models.DecimalField(max_digits=12, decimal_places=2)
    amort_plan = models.TextField()
    owner_tenant = models.ForeignKey(
        "tenants.Tenant", on_delete=models.CASCADE, related_name="erp_assets"
    )
    division = models.CharField(max_length=16, choices=DIVISION_CHOICES, default="BRAVARIJA")

    def __str__(self):
        return f"{self.type_display} - {self.value} € ({self.division_display})"

    @property
    def type_display(self):
        return dict(self.TYPE_CHOICES).get(self.type, self.type)

    @property
    def division_display(self):
        return dict(self.DIVISION_CHOICES).get(self.division, self.division)


class AssetUsage(SoftDeleteModel):
    DIVISION_CHOICES = [
        ("BRAVARIJA", "Bravarija"),
        ("FARBANJE", "Farbanje"),
    ]
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    invoiceable = models.BooleanField(default=True)
    division = models.CharField(max_length=16, choices=DIVISION_CHOICES, default="BRAVARIJA")

    def __str__(self):
        return f"Usage of {self.content_object} (invoiceable: {self.invoiceable}, {self.division_display})"

    @property
    def division_display(self):
        return dict(self.DIVISION_CHOICES).get(self.division, self.division)
