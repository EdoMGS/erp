from decimal import Decimal

from django.db import models
from django.utils.translation import gettext_lazy as _

from ljudski_resursi.models import Employee, RadnaEvaluacija  # Updated import


class Salary(models.Model):
    employee = models.ForeignKey(
        "ljudski_resursi.Employee",
        on_delete=models.CASCADE,
        verbose_name=_("Zaposlenik")
    )
    gross_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name=_("Bruto iznos")
    )
    net_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Neto iznos")
    )
    taxes = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Porezi")
    )
    date = models.DateField(
        verbose_name=_("Datum obračuna plaće"),
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Plaća za {self.employee} - {self.date or ''}"

class SalaryAddition(models.Model):
    ADDITION_TYPES = [
        ('BASE', 'Osnovna plaća'),
        ('VARIABLE', 'Varijabilni dio'),
        ('BONUS', 'Bonus'),
        ('OVERTIME', 'Prekovremeni'),
        ('PERFORMANCE', 'Nagrade za performanse'),
        ('OTHER', 'Ostalo')
    ]

    salary = models.ForeignKey(Salary, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    type = models.CharField(
        max_length=20,
        choices=ADDITION_TYPES,
        default='OTHER'
    )
    date = models.DateField(auto_now_add=True)
    evaluation = models.ForeignKey(
        RadnaEvaluacija,  # Changed from Evaluacija to RadnaEvaluacija
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='salary_additions'
    )
    quality_score = models.ForeignKey(
        'ljudski_resursi.RadnaEvaluacija',  # Changed from OcjenaKvalitete to RadnaEvaluacija
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='quality_score_additions'  # Added unique related_name
    )

    def __str__(self):
        return f"{self.name} ({self.get_type_display()}) for {self.salary.employee}"

class VariablePayCalculation(models.Model):
    employee = models.ForeignKey('ljudski_resursi.Employee', on_delete=models.CASCADE)
    period = models.DateField()
    base_amount = models.DecimalField(max_digits=10, decimal_places=2)
    performance_multiplier = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        default=Decimal('1.00')
    )
    quality_multiplier = models.DecimalField(
        max_digits=3, 
        decimal_places=2,
        default=Decimal('1.00')
    )
    final_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def calculate_final_amount(self):
        self.final_amount = (
            self.base_amount * 
            self.performance_multiplier * 
            self.quality_multiplier
        )
        return self.final_amount

    def save(self, *args, **kwargs):
        if not self.final_amount:
            self.calculate_final_amount()
        super().save(*args, **kwargs)

class Tax(models.Model):
    name = models.CharField(max_length=100)
    rate = models.DecimalField(max_digits=5, decimal_places=2)

    def __str__(self):
        return self.name
