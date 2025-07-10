# skladiste/admin.py

from django.contrib import admin


from .models import (
    Alat,
    Artikl,
    DnevnikDogadaja,
    HTZOprema,
    Izdatnica,
    IzdatnicaStavka,
    Kategorija,
    Lokacija,
    Materijal,
    Primka,
    PrimkaStavka,
    SkladisteResurs,
    Zona,
)


@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ("naziv",)
    search_fields = ("naziv",)
    ordering = ("naziv",)


@admin.register(Lokacija)
class LokacijaAdmin(admin.ModelAdmin):
    list_display = ("naziv", "zona")
    search_fields = ("naziv", "zona__naziv")
    list_filter = ("zona",)
    ordering = ("naziv",)


@admin.register(Artikl)
class ArtiklAdmin(admin.ModelAdmin):
    list_display = [
        "naziv",
        "sifra",
        "trenutna_kolicina",
        "jm",
        "kategorija",
        "dobavljac",
        "lokacija",
    ]
    list_filter = ["kategorija", "dobavljac", "lokacija", "is_active"]
    search_fields = ["naziv", "sifra"]
    list_per_page = 20


@admin.register(Materijal)
class MaterijalAdmin(admin.ModelAdmin):
    list_display = ("naziv", "artikl", "status", "kolicina", "cijena")
    search_fields = ("naziv", "artikl__naziv")
    list_filter = ("status", "datum_dostave")
    ordering = ("-datum_dostave",)


@admin.register(Alat)
class AlatAdmin(admin.ModelAdmin):
    list_display = (
        "naziv",
        "inventarski_broj",
        "zaduzen",
        "is_assigned",
        "assigned_to",
    )
    search_fields = ("naziv", "inventarski_broj")
    list_filter = ("zaduzen", "is_assigned")
    ordering = ("naziv",)


@admin.register(HTZOprema)
class HTZOpremaAdmin(admin.ModelAdmin):
    list_display = (
        "vrsta",
        "stanje",
        "is_assigned",
        "assigned_to",
        "htz_equipment_tracking",
    )
    search_fields = ("vrsta", "stanje")
    list_filter = ("is_assigned", "htz_equipment_tracking")
    ordering = ("vrsta",)


@admin.register(DnevnikDogadaja)
class DnevnikDogadajaAdmin(admin.ModelAdmin):
    list_display = ("datum", "dogadaj", "artikl")
    search_fields = ("dogadaj", "artikl__naziv")
    list_filter = ("datum",)
    ordering = ("-datum",)


@admin.register(SkladisteResurs)
class SkladisteResursAdmin(admin.ModelAdmin):
    list_display = ("naziv", "kolicina", "lokacija")
    search_fields = ("naziv", "lokacija")
    ordering = ("naziv",)


@admin.register(Kategorija)
class KategorijaAdmin(admin.ModelAdmin):
    list_display = ["naziv", "parent", "is_active"]
    list_filter = ["is_active", "parent"]
    search_fields = ["naziv", "opis"]
    list_per_page = 20


class PrimkaStavkaInline(admin.TabularInline):
    model = PrimkaStavka
    extra = 1


@admin.register(Primka)
class PrimkaAdmin(admin.ModelAdmin):
    list_display = ["broj_primke", "datum", "dobavljac", "created_by"]
    list_filter = ["datum", "dobavljac"]
    search_fields = ["broj_primke", "napomena"]
    inlines = [PrimkaStavkaInline]


class IzdatnicaStavkaInline(admin.TabularInline):
    model = IzdatnicaStavka
    extra = 1


@admin.register(Izdatnica)
class IzdatnicaAdmin(admin.ModelAdmin):
    list_display = ["broj_izdatnice", "datum", "preuzeo", "created_by"]
    list_filter = ["datum", "preuzeo"]
    search_fields = ["broj_izdatnice", "napomena"]
    inlines = [IzdatnicaStavkaInline]
