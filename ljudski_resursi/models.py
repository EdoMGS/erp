# ljudski_resursi/models.py

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.utils import timezone

# Koristimo CustomUser
from django.conf import settings
from common.choices import OCJENE_CHOICES

##############################################
# 1) HIERARCHICAL LEVEL
##############################################
class HierarchicalLevel(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Naziv hijerarhijskog nivoa")
    )
    level = models.IntegerField(
        verbose_name=_("Razina (Level)"),
        help_text=_("Niža vrijednost = viši rang, ili obrnuto, ovisno o konvenciji.")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Opis hijerarhijskog nivoa")
    )

    def __str__(self):
        return f"{self.name} (level={self.level})"

    class Meta:
        verbose_name = _("Hierarchical Level")
        verbose_name_plural = _("Hierarchical Levels")
        ordering = ['level', 'name']


##############################################
# 2) DEPARTMENT
##############################################
class Department(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Naziv odjela")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Opis odjela")
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subdepartments',
        verbose_name=_("Nadređeni odjel")
    )
    manager = models.ForeignKey(
        'ljudski_resursi.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_departments',
        verbose_name=_("Voditelj odjela")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Department")
        verbose_name_plural = _("Departments")
        ordering = ['name']


##############################################
# 3) EXPERTISE LEVEL
##############################################
class ExpertiseLevel(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Expertise Level")
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Description")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Expertise Level")
        verbose_name_plural = _("Expertise Levels")


##############################################
# 4) POSITION
##############################################
class Position(models.Model):
    title = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Naziv pozicije")
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Odjel")
    )
    hierarchical_level = models.ForeignKey(
        HierarchicalLevel,
        on_delete=models.CASCADE,
        related_name='positions',
        verbose_name=_("Hijerarhijski nivo")
    )
    is_managerial = models.BooleanField(
        default=False,
        verbose_name=_("Menadžerska pozicija")
    )
    expertise_level = models.ForeignKey(
        ExpertiseLevel,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name=_("Razina stručnosti (default)")
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("Position")
        verbose_name_plural = _("Positions")
        ordering = ['title']


##############################################
# 5) EMPLOYEE
##############################################
class Employee(models.Model):
    """
    Model koji povezuje CustomUser i podatke o zaposleniku.
    """
    ACCESS_LEVEL_CHOICES = [
        ("Direktor", "Direktor"),
        ("Administrator", "Administrator"),
        ("Voditelj Projekta", "Voditelj Projekta"),
        ("Voditelj Proizvodnje", "Voditelj Proizvodnje"),
        ("Nabava", "Nabava"),
        ("Projektant", "Projektant"),
        ("Radnik", "Radnik"),
        ("Skladištar", "Skladištar"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # 'accounts.CustomUser'
        on_delete=models.CASCADE,
        related_name="employee_profile",
        verbose_name=_("User")
    )
    first_name = models.CharField(max_length=50, verbose_name=_("Ime"))
    last_name = models.CharField(max_length=50, verbose_name=_("Prezime"))
    email = models.EmailField(blank=True, null=True, verbose_name=_("Email"), unique=True)

    department = models.ForeignKey(
        'ljudski_resursi.Department',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Department")
    )
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        verbose_name=_("Pozicija")
    )
    manager = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinates',
        verbose_name=_("Nadređeni")
    )

    expertise_level = models.ForeignKey(
        ExpertiseLevel,
        on_delete=models.PROTECT,
        related_name='employees',
        verbose_name=_("Expertise Level")
    )
    hierarchical_level = models.PositiveIntegerField(default=1, verbose_name=_("Hierarchical Level"))

    is_active = models.BooleanField(default=True, verbose_name=_("Aktivan"))

    tax_configuration = models.ForeignKey(
        'financije.TaxConfiguration',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Tax Configuration")
    )
    salary_coefficient = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=1.0,
        verbose_name=_("Salary Coefficient")
    )

    onboarding_date = models.DateField(null=True, blank=True, verbose_name=_("Onboarding Date"))
    onboarding_timeline = models.PositiveIntegerField(null=True, blank=True, verbose_name=_("Onboarding Timeline (days)"))
    employee_satisfaction = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True,
                                                verbose_name=_("Employee Satisfaction"))
    satisfaction_score = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True,
                                             verbose_name=_("Satisfaction Score"))

    access_level = models.CharField(
        max_length=50,
        choices=ACCESS_LEVEL_CHOICES,
        default="Radnik",
        verbose_name=_("Razina pristupa"),
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.user.username}"

    def calculate_performance_metrics(self, period):
        """Returns performance metrics for variable pay calculation"""
        from financije.models import VariablePayCalculation
        
        evaluations = self.evaluacije.filter(
            evaluation_period__lte=period
        ).order_by('-evaluation_period')[:3]
        
        if not evaluations.exists():
            return Decimal('1.00')  # Default multiplier
            
        avg_score = sum(e.ocjena for e in evaluations) / len(evaluations)
        quality_scores = self.ocjene_kvalitete.filter(
            radni_nalog__datum_zavrsetka__lte=period
        ).aggregate(avg=models.Avg('ocjena'))['avg'] or Decimal('3.00')
        
        return {
            'performance_multiplier': Decimal(str(avg_score / 5.0)),
            'quality_multiplier': Decimal(str(quality_scores / 5.0))
        }

    def get_current_variable_pay(self):
        """Gets current variable pay amount"""
        rule = self.get_variable_pay_rule()
        if not rule:
            return Decimal('0.00')
        
        metrics = self.calculate_performance_metrics(timezone.now())
        base = rule.variable_pay
        
        return base * metrics['performance_multiplier'] * metrics['quality_multiplier']

    def update_quality_metrics(self, quality_assessment):
        """Updates employee metrics based on quality assessment"""
        from financije.models import VariablePayCalculation
        metrics = self.calculate_performance_metrics(timezone.now())
        
        VariablePayCalculation.objects.create(
            employee=self,
            period=quality_assessment.radni_nalog.datum_zavrsetka,
            base_amount=self.get_variable_pay_rule().variable_pay,
            performance_multiplier=metrics['performance_multiplier'],
            quality_multiplier=metrics['quality_multiplier']
        )

    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")
        ordering = ['last_name', 'first_name']


##############################################
# 6) JOB POSITION (ako se još koristi)
##############################################
class JobPosition(models.Model):
    """
    Ako ti ne treba duplikat, možda ga izbaciti.
    """
    title = models.CharField(max_length=255, verbose_name=_("Job Title"))
    description = models.TextField(blank=True, null=True, verbose_name=_("Description"))
    department = models.ForeignKey(
        'ljudski_resursi.Department',
        on_delete=models.CASCADE,
        related_name="job_positions",
        verbose_name=_("Department")
    )
    level = models.PositiveIntegerField(default=1, verbose_name=_("Level"))

    def __str__(self):
        return f"{self.title} in {self.department.name}"


##############################################
# 7) EVALUACIJA
##############################################
# Removed the old 'Evaluacija' model

##############################################
# 8) OCJENA KVALITETE
##############################################
# Removed the duplicate 'OcjenaKvalitete(models.Model)' definition

class Nagrada(models.Model):
    """Model for employee rewards/bonuses tied to work orders"""
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='nagrade',
        verbose_name=_("Zaposlenik")
    )
    radni_nalog = models.ForeignKey(
        'proizvodnja.RadniNalog',
        on_delete=models.CASCADE,
        related_name='nagrade',
        verbose_name=_("Radni nalog")
    )
    iznos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Iznos nagrade (€)")
    )
    razlog = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Razlog nagrade")
    )
    datum_dodjele = models.DateField(
        auto_now_add=True,
        verbose_name=_("Datum dodjele")
    )
    odobrio = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        null=True,
        related_name='odobrene_nagrade',
        verbose_name=_("Odobrio")
    )

    class Meta:
        verbose_name = _("Nagrada")
        verbose_name_plural = _("Nagrade")
        ordering = ['-datum_dodjele']

    def __str__(self):
        return f"Nagrada {self.iznos}€ za {self.employee} ({self.radni_nalog})"


class RadnaEvaluacija(models.Model):
    """Monthly/quarterly employee evaluations"""
    employee = models.ForeignKey('Employee', on_delete=models.CASCADE, related_name='evaluacije')
    evaluator = models.ForeignKey('Employee', related_name='dane_evaluacije', on_delete=models.CASCADE)
    evaluation_period = models.CharField(max_length=50)  # renamed from 'period'
    datum_evaluacije = models.DateTimeField(auto_now_add=True)
    
    # Core competencies (1-5 scale)
    efikasnost = models.IntegerField(choices=OCJENE_CHOICES)
    kvaliteta_rada = models.IntegerField(choices=OCJENE_CHOICES)
    timski_rad = models.IntegerField(choices=OCJENE_CHOICES)
    inicijativa = models.IntegerField(choices=OCJENE_CHOICES)
    
    # Additional metrics
    broj_zavrsenih_naloga = models.IntegerField(default=0)
    prosjecna_ocjena_kvalitete = models.DecimalField(max_digits=3, decimal_places=2, null=True)
    ukupno_sati_rada = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    
    komentar = models.TextField(blank=True)
    preporuke = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['employee', 'evaluation_period']
