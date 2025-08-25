from django.db import models

from tenants.models import Tenant


# Minimal stub models referenced by historical migrations elsewhere.
# Only primary keys provided; fields can be expanded if needed for runtime.


class RadniNalog(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    quote_id = models.IntegerField()
    option = models.CharField(max_length=16)

    class Meta:
        unique_together = [("tenant", "quote_id", "option")]


class Projekt(models.Model):
    pass


class TipVozila(models.Model):
    pass


class TipProjekta(models.Model):
    pass


class ProizvodniResurs(models.Model):
    pass


class Grupaposlova(models.Model):
    pass


class TemplateRadniNalog(models.Model):
    pass


class Angazman(models.Model):
    pass
