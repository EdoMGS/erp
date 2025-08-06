# proizvodnja/admin.py

from django.contrib import admin

from .forms import (
    AngazmanForm,
    DodatniAngazmanForm,
    GrupaPoslovaForm,
    NotifikacijaForm,
    OcjenaKvaliteteForm,
    PovijestPromjenaForm,
    ProizvodniResursForm,
    ProizvodnjaForm,
    ProjektForm,
    RadniNalogForm,
    RadniNalogMaterijalForm,
    TemplateRadniNalogForm,
    TipProjektaForm,
    TipVozilaForm,
    UstedaForm,
    VideoMaterijalForm,
    VideoPitanjeForm,
)
from .models import (
    Angazman,
    DodatniAngazman,
    GrupaPoslova,
    MonthlyWorkRecord,
    Notifikacija,
    OcjenaKvalitete,
    PovijestPromjena,
    ProizvodniResurs,
    Proizvodnja,
    Projekt,
    RadniNalog,
    RadniNalogMaterijal,
    TemplateRadniNalog,
    TipProjekta,
    TipVozila,
    Usteda,
    VideoMaterijal,
    VideoPitanje,
)


###############################################################################
# 1) TIP PROJEKTA, TIP VOZILA, GRUPA POSLOVA
###############################################################################
@admin.register(TipProjekta)
class TipProjektaAdmin(admin.ModelAdmin):
    form = TipProjektaForm
    list_display = ("naziv", "opis", "aktivan")
    search_fields = ("naziv",)
    list_filter = ("aktivan",)
    ordering = ("naziv",)


@admin.register(TipVozila)
class TipVozilaAdmin(admin.ModelAdmin):
    form = TipVozilaForm
    list_display = ("naziv", "opis", "aktivan")
    search_fields = ("naziv",)
    list_filter = ("aktivan",)
    ordering = ("naziv",)


@admin.register(GrupaPoslova)
class GrupaPoslovaAdmin(admin.ModelAdmin):
    form = GrupaPoslovaForm
    list_display = ("naziv", "opis", "tip_projekta")
    search_fields = ("naziv",)
    list_filter = ("tip_projekta",)
    ordering = ("naziv",)


###############################################################################
# 2) PROJEKT
###############################################################################
@admin.register(Projekt)
class ProjektAdmin(admin.ModelAdmin):
    form = ProjektForm
    readonly_fields = ("created_at", "updated_at", "erp_id", "get_financial_summary")
    list_display = (
        "naziv_projekta",
        "status",
        "pocetak_projekta",
        "rok_za_isporuku",
        "get_financial_summary",
    )
    search_fields = ("naziv_projekta", "erp_id")
    list_filter = ("status", "tip_projekta", "tip_vozila")
    ordering = ("-pocetak_projekta",)

    def get_financial_summary(self, obj):
        if obj.financial_details:
            return f"Net: {obj.financial_details.contracted_net_price}, Gross: {obj.financial_details.contracted_gross_price}"
        return "No financial details"

    get_financial_summary.short_description = "Financial Summary"


###############################################################################
# 3) TEMPLATE RADNI NALOG
###############################################################################
@admin.register(TemplateRadniNalog)
class TemplateRadniNalogAdmin(admin.ModelAdmin):
    form = TemplateRadniNalogForm
    list_display = (
        "naziv_naloga",
        "tip_projekta",
        "tip_vozila",
        "grupa_posla",
        "sort_index",
    )
    search_fields = ("naziv_naloga",)
    list_filter = ("tip_projekta", "tip_vozila", "grupa_posla")


###############################################################################
# 4) PROIZVODNJA
###############################################################################
@admin.register(Proizvodnja)
class ProizvodnjaAdmin(admin.ModelAdmin):
    form = ProizvodnjaForm
    list_display = ("naziv", "projekt", "status", "datum_pocetka", "datum_zavrsetka")
    search_fields = ("naziv", "projekt__naziv_projekta")
    list_filter = ("status", "projekt")
    ordering = ("-datum_pocetka",)


###############################################################################
# 5) INLINE KLASE
###############################################################################
class AngazmanInline(admin.TabularInline):
    model = Angazman
    form = AngazmanForm
    extra = 1


class RadniNalogMaterijalInline(admin.TabularInline):
    model = RadniNalogMaterijal
    form = RadniNalogMaterijalForm
    extra = 1


class OcjenaKvaliteteInline(admin.TabularInline):
    model = OcjenaKvalitete
    form = OcjenaKvaliteteForm
    extra = 1
    fields = [
        "ocjenjivac",
        "employee",
        "kvaliteta_izvedbe",
        "postivanje_procedura",
        "efikasnost_rada",
        "slike",
        "video",
        "komentar",
    ]


class VideoMaterijalInline(admin.TabularInline):
    model = VideoMaterijal
    form = VideoMaterijalForm
    extra = 1


class VideoPitanjeInline(admin.TabularInline):
    model = VideoPitanje
    form = VideoPitanjeForm
    extra = 1


class PovijestPromjenaInline(admin.TabularInline):
    model = PovijestPromjena
    form = PovijestPromjenaForm
    extra = 1


class UstedaInline(admin.StackedInline):
    """
    OneToOne veza s RadniNalog -> zato StackedInline i max_num=1.
    """

    model = Usteda
    form = UstedaForm
    can_delete = False
    extra = 0
    max_num = 1


# Removed RadniProcesInline and OpremaInline since the models do not exist


###############################################################################
# 6) RADNI NALOG
###############################################################################
@admin.register(RadniNalog)
class RadniNalogAdmin(admin.ModelAdmin):
    form = RadniNalogForm
    readonly_fields = ("created_at", "updated_at", "broj_naloga")
    list_display = (
        "naziv_naloga",
        "projekt",
        "status",
        "postotak_napretka",
        "predvidjeno_vrijeme",
        "stvarno_vrijeme",
    )
    search_fields = ("naziv_naloga", "projekt__naziv_projekta")
    list_filter = ("status", "prioritet", "tip_posla")
    ordering = ("-datum_pocetka",)

    inlines = [
        AngazmanInline,
        RadniNalogMaterijalInline,
        OcjenaKvaliteteInline,
        VideoMaterijalInline,
        VideoPitanjeInline,
        PovijestPromjenaInline,
        UstedaInline,
        # Removed RadniProcesInline and OpremaInline from inlines
    ]


###############################################################################
# 7) OSTALE REGISTRACIJE MODELA
###############################################################################
@admin.register(RadniNalogMaterijal)
class RadniNalogMaterijalAdmin(admin.ModelAdmin):
    form = RadniNalogMaterijalForm
    list_display = (
        "radni_nalog",
        "materijal",
        "kolicina",
    )  # Changed 'artikl' to 'materijal'
    search_fields = (
        "radni_nalog__naziv_naloga",
        "materijal__naziv",
    )  # Changed 'artikl' to 'materijal'
    list_filter = ("materijal",)  # Changed 'artikl' to 'materijal'


@admin.register(Angazman)
class AngazmanAdmin(admin.ModelAdmin):
    form = AngazmanForm
    list_display = ("radni_nalog", "employee", "sati_rada", "status", "datum_angazmana")
    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "radni_nalog__naziv_naloga",
    )
    list_filter = ("status",)


@admin.register(DodatniAngazman)
class DodatniAngazmanAdmin(admin.ModelAdmin):
    form = DodatniAngazmanForm
    list_display = ("angazman", "employee", "sati_rada")
    search_fields = (
        "employee__first_name",
        "employee__last_name",
        "angazman__radni_nalog__naziv_naloga",
    )


@admin.register(OcjenaKvalitete)
class OcjenaKvaliteteAdmin(admin.ModelAdmin):
    form = OcjenaKvaliteteForm
    list_display = [
        "radni_nalog",
        "ocjenjivac",
        "employee",
        "kvaliteta_izvedbe",
        "postivanje_procedura",
        "efikasnost_rada",
        "datum_ocjene",
    ]
    fields = [
        "radni_nalog",
        "ocjenjivac",
        "employee",
        "kvaliteta_izvedbe",
        "postivanje_procedura",
        "efikasnost_rada",
        "predvidjeno_vrijeme",
        "stvarno_vrijeme",
        "slike",
        "video",
        "komentar",
        "tezinski_faktor",
    ]
    readonly_fields = ["datum_ocjene"]


@admin.register(VideoMaterijal)
class VideoMaterijalAdmin(admin.ModelAdmin):
    form = VideoMaterijalForm
    list_display = ("naziv", "radni_nalog", "datum_dodavanja")
    search_fields = ("naziv", "radni_nalog__naziv_naloga")
    list_filter = ("datum_dodavanja",)


@admin.register(VideoPitanje)
class VideoPitanjeAdmin(admin.ModelAdmin):
    form = VideoPitanjeForm
    list_display = ("radni_nalog", "opis")
    search_fields = ("radni_nalog__naziv_naloga", "opis")


@admin.register(Notifikacija)
class NotifikacijaAdmin(admin.ModelAdmin):
    form = NotifikacijaForm
    list_display = ("korisnik", "poruka", "procitano", "prioritet", "tip")
    search_fields = ("korisnik__username", "poruka")
    list_filter = ("prioritet", "tip", "procitano")


@admin.register(PovijestPromjena)
class PovijestPromjenaAdmin(admin.ModelAdmin):
    form = PovijestPromjenaForm
    list_display = ("id", "get_radni_nalog", "content_type", "object_id", "user")

    def get_radni_nalog(self, obj):
        if hasattr(obj.object_ref, "radni_nalog"):
            return obj.object_ref.radni_nalog
        return None

    get_radni_nalog.short_description = "Radni Nalog"


@admin.register(MonthlyWorkRecord)
class MonthlyWorkRecordAdmin(admin.ModelAdmin):
    list_display = ("employee", "year", "month", "hours_worked")
    search_fields = ("employee__first_name", "employee__last_name")
    list_filter = ("year", "month")


@admin.register(Usteda)
class UstedaAdmin(admin.ModelAdmin):
    form = UstedaForm
    list_display = (
        "radni_nalog",
        "predvidjeno_vrijeme",
        "stvarno_vrijeme",
        "usteda_sati",
        "dodatna_nagrada",
    )
    search_fields = ("radni_nalog__naziv_naloga",)


@admin.register(ProizvodniResurs)
class ProizvodniResursAdmin(admin.ModelAdmin):
    form = ProizvodniResursForm
    list_display = ("id", "naziv", "tip", "kolicina", "dostupnost")
    search_fields = ("naziv", "tip")
    list_filter = ("tip", "dostupnost")
