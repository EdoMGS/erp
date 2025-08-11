# client/models.py

from django.core.validators import RegexValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.tenants import TenantManager


class ClientSupplier(models.Model):
    tenant_id = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="subclients",
        verbose_name=_("Tenant (Holding/Operativa)"),
    )
    RELATIONSHIP_STATUS_CHOICES = [
        ("active", _("Aktivan")),
        ("inactive", _("Neaktivan")),
        ("prospective", _("Potencijalni")),
        ("former", _("Bivši")),
        ("blocked", _("Blokiran")),
    ]

    LOYALTY_LEVELS = [
        ("bronze", _("Bronze")),
        ("silver", _("Silver")),
        ("gold", _("Gold")),
        ("platinum", _("Platinum")),
    ]

    name = models.CharField(
        max_length=255,
        verbose_name=_("Naziv (ime tvrtke ili osobe)"),
        db_index=True,  # Add index for frequent searches
    )
    address = models.TextField(verbose_name=_("Adresa"))
    email = models.EmailField(
        verbose_name=_("Email"),
        validators=[
            RegexValidator(
                regex=r"^[\w\.-]+@[\w\.-]+\.\w+$",
                message=_("Unesite ispravan email format."),
                code="invalid_email",
            )
        ],
    )
    phone = models.CharField(max_length=20, verbose_name=_("Telefon"))
    is_active = models.BooleanField(default=True, verbose_name=_("Aktivan"))
    is_supplier = models.BooleanField(default=False, verbose_name=_("Dobavljač?"))
    oib = models.CharField(
        max_length=11,
        unique=True,
        verbose_name=_("OIB"),
        validators=[
            RegexValidator(
                regex=r"^\d{11}$",
                message=_("OIB mora imati točno 11 znamenki."),
                code="invalid_oib",
            )
        ],
    )
    country = models.CharField(max_length=100, verbose_name=_("Država"), default="Hrvatska")
    city = models.CharField(max_length=100, verbose_name=_("Grad"))
    postal_code = models.CharField(max_length=10, verbose_name=_("Poštanski broj"))
    county = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Županija"))
    long_term_relationship = models.BooleanField(default=False, verbose_name=_("Dugoročni odnos"))
    relationship_status = models.CharField(
        max_length=20,
        choices=RELATIONSHIP_STATUS_CHOICES,
        default="active",
        verbose_name=_("Status odnosa"),
    )

    date_created = models.DateTimeField(auto_now_add=True, verbose_name=_("Datum kreiranja"))
    date_updated = models.DateTimeField(auto_now=True, verbose_name=_("Datum ažuriranja"))

    # Multi-tenant manager
    objects = models.Manager()
    tenant_objects = TenantManager()

    def __str__(self):
        tip = _("Dob.") if self.is_supplier else _("Klijent")
        return f"{self.name} ({tip})"

    class Meta:
        verbose_name = _("Klijent/Dobavljač")
        verbose_name_plural = _("Klijenti/Dobavljači")
        indexes = [
            models.Index(fields=["name", "email"]),
            models.Index(fields=["oib"]),
            models.Index(fields=["relationship_status", "is_active"]),
        ]
        ordering = ["name"]

    def get_list_fields(self):
        """Return fields for list view display"""
        return [
            self.name,
            self.email,
            self.phone,
            self.get_relationship_status_display(),
        ]


class ClientProfile(models.Model):
    client = models.OneToOneField("client.ClientSupplier", on_delete=models.CASCADE, related_name="clientprofile")
    loyalty_level = models.CharField(
        max_length=20,
        choices=ClientSupplier.LOYALTY_LEVELS,
        default="bronze",
        verbose_name=_("Razina lojalnosti"),
    )
    feedback = models.TextField(null=True, blank=True, verbose_name=_("Povratne informacije"))
    post_sales_feedback = models.TextField(null=True, blank=True, verbose_name=_("Post-prodajne povratne informacije"))

    class Meta:
        verbose_name = _("Profil klijenta")
        verbose_name_plural = _("Profili klijenata")


class CityPostalCode(models.Model):
    postal_code = models.CharField(
        max_length=10,
        validators=[RegexValidator(r"^\d{5}$")],
        unique=True,
        verbose_name=_("Postal Code"),
    )
    city = models.CharField(max_length=255, verbose_name=_("City"))
    district = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Naselje"))
    county = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Županija"))

    def __str__(self):
        return f"{self.city} - {self.postal_code}"

    class Meta:
        verbose_name = _("Poštanski broj")
        verbose_name_plural = _("Poštanski brojevi")
        unique_together = ["postal_code", "city"]
        indexes = [
            models.Index(fields=["postal_code"]),
            models.Index(fields=["city"]),
        ]


class ClientActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ("create", _("Kreiranje")),
        ("update", _("Ažuriranje")),
        ("delete", _("Brisanje")),
        ("status_change", _("Promjena statusa")),
        ("other", _("Ostalo")),
    ]

    client = models.ForeignKey(
        ClientSupplier,
        on_delete=models.CASCADE,
        related_name="activity_logs",
        verbose_name=_("Klijent/Dobavljač"),
    )
    activity = models.TextField(verbose_name=_("Activity Description"))
    timestamp = models.DateTimeField(default=timezone.now, db_index=True, verbose_name=_("Timestamp"))
    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPES,
        default="other",
        verbose_name=_("Tip aktivnosti"),
    )

    def __str__(self):
        return f"Activity for {self.client.name} at {self.timestamp}"

    class Meta:
        verbose_name = _("Log aktivnosti")
        verbose_name_plural = _("Logovi aktivnosti")
        indexes = [
            models.Index(fields=["-timestamp"]),
            models.Index(fields=["client", "-timestamp"]),
        ]
        ordering = ["-timestamp"]


# Signals
@receiver(post_save, sender=ClientSupplier)
def create_client_profile(sender, instance, created, **kwargs):
    """Create ClientProfile when a new ClientSupplier is created"""
    if created and not instance.is_supplier:
        ClientProfile.objects.create(client=instance)


@receiver(post_save, sender=ClientSupplier)
def save_client_profile(sender, instance, **kwargs):
    """Update ClientProfile when ClientSupplier is updated"""
    if not instance.is_supplier and hasattr(instance, "clientprofile"):
        instance.clientprofile.save()
