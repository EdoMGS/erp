from decimal import Decimal

from django.db import models


class JobCost(models.Model):
    DIVISION_CHOICES = [
        ("BRAVARIJA", "Bravarija"),
        ("FARBANJE", "Farbanje"),
    ]
    name = models.CharField(max_length=255)
    cost_50 = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    owner_20 = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    workers_30 = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    total_cost = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal("0.00"))
    is_paid = models.BooleanField(default=False, help_text="Is this job paid by the client?")
    paid_at = models.DateTimeField(null=True, blank=True)
    division = models.CharField(max_length=16, choices=DIVISION_CHOICES, default="BRAVARIJA")

    def __str__(self):
        return f"{self.name} ({self.division_display})"

    @property
    def division_display(self):
        return dict(self.DIVISION_CHOICES).get(self.division, self.division)


class FondRadnici(models.Model):
    ROLE_CHOICES = [
        ("majstor", "Majstor"),
        ("pomocni", "Pomoćni"),
        ("mentor", "Mentor"),
    ]
    DIVISION_CHOICES = [
        ("BRAVARIJA", "Bravarija"),
        ("FARBANJE", "Farbanje"),
    ]
    job_cost = models.ForeignKey(JobCost, related_name="fond_radnici", on_delete=models.CASCADE)
    worker_name = models.CharField(max_length=255)
    hours = models.DecimalField(max_digits=6, decimal_places=2)
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default="pomocni")
    division = models.CharField(max_length=16, choices=DIVISION_CHOICES, default="BRAVARIJA")
    quality_ok = models.BooleanField(default=True, help_text="Is the job done without errors?")
    bonus = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Extra reward for bringing a client or mentoring",
    )
    penalty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        help_text="Penalty for mistakes or rule violations",
    )

    def __str__(self):
        return f"{self.worker_name} ({self.hours}h, {self.role_display}, {self.division_display})"

    @property
    def role_display(self):
        return dict(self.ROLE_CHOICES).get(self.role, self.role)

    @property
    def division_display(self):
        return dict(self.DIVISION_CHOICES).get(self.division, self.division)
