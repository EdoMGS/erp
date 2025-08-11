from django.db import models


class Tenant(models.Model):
    name = models.CharField(max_length=120)
    subdomain = models.CharField(max_length=80, unique=True)

    def __str__(self):
        return self.name
