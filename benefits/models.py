from django.db import models

# Create your models here.


class Meal(models.Model):
    employee_name = models.CharField(max_length=255)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.employee_name} - {self.date}"


class Travel(models.Model):
    employee_name = models.CharField(max_length=255)
    destination = models.CharField(max_length=255)
    date = models.DateField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.employee_name} - {self.destination}"


class Bonus(models.Model):
    employee_name = models.CharField(max_length=255)
    year = models.PositiveIntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.employee_name} - {self.year}"
