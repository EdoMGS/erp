"""Minimal stub models for historical migration dependencies (skladiste app).

This file intentionally provides only empty placeholder models required for
other apps' existing migration dependencies. Do not reintroduce legacy
business logic here; add new fields via forward migrations if needed.
"""

from django.db import models


class Artikl(models.Model):
    pass


class Zona(models.Model):
    pass


class Materijal(models.Model):
    pass


class Primka(models.Model):
    pass
