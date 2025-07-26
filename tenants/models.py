from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=100)
    domain = models.CharField(max_length=255, unique=True, verbose_name="Domain")

    def __str__(self):
        return self.name
