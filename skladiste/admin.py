# skladiste/admin.py

from django.contrib import admin

from .models import Artikl, Materijal, Primka, Zona


@admin.register(Artikl)
class ArtiklAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(Materijal)
class MaterijalAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(Primka)
class PrimkaAdmin(admin.ModelAdmin):
    list_display = ("id",)
