# accounts/models.py

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import BaseModel


class CustomUser(AbstractUser):
    """
    Minimalno prilagođeni User.
    Uklonili smo polje 'department' kako bismo izbjegli kružnu ovisnost
    (Employee -> CustomUser -> Department -> Employee).
    """

    email = models.EmailField(unique=True, verbose_name=_("Email Address"))
    phone_number = models.CharField(max_length=15, blank=True, null=True)

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="customuser_set",
        blank=True,
        help_text=_("The groups this user belongs to."),
        verbose_name=_("groups"),
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        related_name="customuser_set",
        blank=True,
        help_text=_("Specific permissions for this user."),
        verbose_name=_("user permissions"),
    )

    # Ako želiš role, mozes dodati many-to-many
    # roles = models.ManyToManyField('common.Role', blank=True, related_name='users')

    def __str__(self):
        return f"{self.username} ({self.email})"


class Employee(BaseModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="employees"
    )
    company = models.ForeignKey(
        "core.Company", on_delete=models.CASCADE, related_name="employees"
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    oib = models.CharField(max_length=25, blank=True, null=True)
    iban = models.CharField(max_length=34, blank=True, null=True)
    role = models.CharField(max_length=100, blank=True)
    salary_base = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    joined_at = models.DateField(null=True, blank=True)
    left_at = models.DateField(null=True, blank=True)
    cost_center_code = models.CharField(max_length=50, blank=True, null=True)
    is_foreign = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CostCenter(BaseModel):
    WORKER = "worker"
    VEHICLE = "vehicle"
    TOOL = "tool"
    SPACE = "space"
    TYPE_CHOICES = [
        (WORKER, "radnik"),
        (VEHICLE, "vozilo"),
        (TOOL, "alat"),
        (SPACE, "prostor"),
    ]

    code = models.CharField(max_length=50)
    description = models.CharField(max_length=255, blank=True)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    company = models.ForeignKey(
        "core.Company", on_delete=models.CASCADE, related_name="cost_centers"
    )

    class Meta:
        unique_together = ("company", "code")

    def __str__(self):
        return f"{self.code} - {self.description}"


class Account(BaseModel):
    ASSET = "asset"
    LIABILITY = "liability"
    EXPENSE = "expense"
    INCOME = "income"
    TYPE_CHOICES = [
        (ASSET, "asset"),
        (LIABILITY, "liability"),
        (EXPENSE, "expense"),
        (INCOME, "income"),
    ]

    code = models.CharField(max_length=50)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    company = models.ForeignKey(
        "core.Company", on_delete=models.CASCADE, related_name="accounts"
    )

    class Meta:
        unique_together = ("company", "code")

    def __str__(self):
        return f"{self.code} - {self.name}"
