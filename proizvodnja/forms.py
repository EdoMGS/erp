# proizvodnja/forms.py


from django import forms
from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from ljudski_resursi.models import Employee

from .models import (Angazman, DodatniAngazman, GrupaPoslova,
                     MonthlyWorkRecord, Notifikacija, OcjenaKvalitete,
                     PovijestPromjena, ProizvodniResurs, Proizvodnja, Projekt,
                     RadniNalog, RadniNalogMaterijal, TemplateRadniNalog,
                     TipProjekta, TipVozila, Usteda, VideoMaterijal,
                     VideoPitanje)

User = get_user_model()


def get_materijal_formset():
    """Factory function to create MaterialFormSet on demand"""
    from proizvodnja.models import RadniNalog
    from skladiste.models import Materijal

    return inlineformset_factory(
        RadniNalog,
        Materijal,
        fields=("artikl", "kolicina", "status"),
        extra=1,
        can_delete=True,
    )


def get_radni_nalog_materijal_formset():
    """Factory function to create formset for RadniNalog and Materijal"""

    from .models import RadniNalog, RadniNalogMaterijal

    return inlineformset_factory(
        RadniNalog,
        RadniNalogMaterijal,
        form=RadniNalogMaterijalForm,
        fields=("materijal", "kolicina"),
        extra=1,
        can_delete=True,
    )


###############################################################################
# 1) BAZNA FORMA
###############################################################################
class BaseModelForm(forms.ModelForm):
    """
    Zajednička poboljšanja i widgeti za sve forme:
    - Zadani 'form-control' CSS za polja (Bootstrap).
    - Mjesto za common clean() logiku.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if "class" not in field.widget.attrs:
                field.widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


###############################################################################
# 2) TIP PROJEKTA, TIP VOZILA, GRUPA POSLOVA
###############################################################################
class TipProjektaForm(BaseModelForm):
    class Meta:
        model = TipProjekta
        fields = ["naziv", "opis", "aktivan"]


class TipVozilaForm(BaseModelForm):
    class Meta:
        model = TipVozila
        fields = ["naziv", "opis", "aktivan"]


class GrupaPoslovaForm(BaseModelForm):
    class Meta:
        model = GrupaPoslova
        fields = ["naziv", "opis", "tip_projekta"]


###############################################################################
# 3) PROJEKT
###############################################################################
class ProjektForm(BaseModelForm):
    """
    Forma za kreiranje/uređivanje Projekta.
    """

    class Meta:
        model = Projekt
        fields = [
            "naziv_projekta",
            "erp_id",
            "opis",
            "pocetak_projekta",
            "rok_za_isporuku",
            "tip_projekta",
            "tip_vozila",
            "status",
            "ugradnja_na_lokaciji",
            "ručni_unos_radnih_naloga",
            "financial_details",
        ]
        widgets = {
            "pocetak_projekta": forms.DateInput(attrs={"type": "date"}),
            "rok_za_isporuku": forms.DateInput(attrs={"type": "date"}),
        }


###############################################################################
# 4) TEMPLATE RADNI NALOG
###############################################################################
class TemplateRadniNalogForm(BaseModelForm):
    class Meta:
        model = TemplateRadniNalog
        fields = [
            "tip_projekta",
            "tip_vozila",
            "grupa_posla",
            "naziv_naloga",
            "opis_naloga",
            "default_predvidjeno_vrijeme",
            "broj_izvrsenja",
            "akumulirani_sati",
            "sort_index",
        ]


###############################################################################
# 5) PROIZVODNJA
###############################################################################
class ProizvodnjaForm(BaseModelForm):
    class Meta:
        model = Proizvodnja
        fields = [
            "projekt",
            "naziv",
            "opis",
            "datum_pocetka",
            "datum_zavrsetka",
            "status",
            "resursi",
            "radni_nalozi",
        ]
        widgets = {
            "datum_pocetka": forms.DateInput(attrs={"type": "date"}),
            "datum_zavrsetka": forms.DateInput(attrs={"type": "date"}),
        }


###############################################################################
# 6) RADNI NALOG
###############################################################################
class RadniNalogForm(BaseModelForm):
    class Meta:
        model = RadniNalog
        fields = [
            "naziv_naloga",
            "projekt",
            "grupa_posla",
            "tip_posla",
            "datum_pocetka",
            "datum_zavrsetka",
            "postotak_napretka",
            "opis",
            "dodatne_osobe",
            "zaduzena_osoba",
            "odgovorna_osoba",
            "prioritet",
            "bypass_materijala",
            "dokumentacija_bypass",
            "status",
            "predvidjeno_vrijeme",
            "stvarno_vrijeme",
            "preduvjeti",
        ]
        widgets = {
            "datum_pocetka": forms.DateInput(attrs={"type": "date"}),
            "datum_zavrsetka": forms.DateInput(attrs={"type": "date"}),
            "opis": forms.Textarea(attrs={"rows": 4}),
        }


###############################################################################
# 7) RADNI NALOG MATERIJAL
###############################################################################
class RadniNalogMaterijalForm(BaseModelForm):
    class Meta:
        model = RadniNalogMaterijal
        fields = ["radni_nalog", "materijal", "kolicina", "template_nalog"]
        widgets = {
            "kolicina": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }

    def clean_kolicina(self):
        kolicina = self.cleaned_data.get("kolicina")
        if kolicina and kolicina < 0:
            raise forms.ValidationError(_("Količina ne može biti negativna."))
        return kolicina


MaterijalFormSet = inlineformset_factory(
    RadniNalog,
    RadniNalogMaterijal,
    form=RadniNalogMaterijalForm,
    extra=1,
    can_delete=True,
    min_num=0,
)


###############################################################################
# 8) ANGAZMAN, DODATNI ANGAZMAN
###############################################################################
class AngazmanForm(BaseModelForm):
    class Meta:
        model = Angazman
        fields = ["employee", "sati_rada", "datum_angazmana", "razlog"]
        widgets = {
            "datum_angazmana": forms.DateInput(attrs={"type": "date"}),
            "razlog": forms.Textarea(attrs={"rows": 3}),
        }


class DodatniAngazmanForm(BaseModelForm):
    class Meta:
        model = DodatniAngazman
        fields = ["angazman", "employee", "sati_rada"]


AngazmanFormSet = inlineformset_factory(
    RadniNalog,
    Angazman,
    form=AngazmanForm,
    extra=1,
    can_delete=True,
)


###############################################################################
# 9) OCJENA KVALITETE
###############################################################################
class OcjenaKvaliteteForm(BaseModelForm):
    class Meta:
        model = OcjenaKvalitete
        fields = [
            "ocjenjivac",
            "employee",
            "kvaliteta_izvedbe",
            "postivanje_procedura",
            "efikasnost_rada",
            "komentar",
            "slike",
            "video",
            "tezinski_faktor",
        ]
        widgets = {
            "komentar": forms.Textarea(attrs={"rows": 3}),
        }


OcjenaKvaliteteFormSet = inlineformset_factory(
    RadniNalog,
    OcjenaKvalitete,
    form=OcjenaKvaliteteForm,
    extra=1,
    can_delete=True,
)


###############################################################################
# 10) UŠTEDA
###############################################################################
class UstedaForm(BaseModelForm):
    class Meta:
        model = Usteda
        fields = ["predvidjeno_vrijeme", "stvarno_vrijeme"]
        widgets = {
            "predvidjeno_vrijeme": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
            "stvarno_vrijeme": forms.NumberInput(attrs={"step": "0.01", "min": "0"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        predvidjeno = cleaned_data.get("predvidjeno_vrijeme")
        stvarno = cleaned_data.get("stvarno_vrijeme")
        if predvidjeno is not None and predvidjeno < 0:
            raise forms.ValidationError(_("Predviđeno vrijeme ne može biti negativno."))
        if stvarno is not None and stvarno < 0:
            raise forms.ValidationError(_("Stvarno vrijeme ne može biti negativno."))
        return cleaned_data


UstedaFormSet = inlineformset_factory(
    RadniNalog,
    Usteda,
    form=UstedaForm,
    extra=1,
    can_delete=False,
    max_num=1,
)


###############################################################################
# 11) VIDEO MATERIJAL, VIDEO PITANJE
###############################################################################
class VideoMaterijalForm(BaseModelForm):
    class Meta:
        model = VideoMaterijal
        fields = ["naziv", "opis", "video_file"]
        widgets = {
            "opis": forms.Textarea(attrs={"rows": 3}),
        }


VideoMaterijalFormSet = inlineformset_factory(
    RadniNalog,
    VideoMaterijal,
    form=VideoMaterijalForm,
    extra=1,
    can_delete=True,
)


class VideoPitanjeForm(BaseModelForm):
    class Meta:
        model = VideoPitanje
        fields = ["video", "opis"]
        widgets = {
            "opis": forms.Textarea(attrs={"rows": 3}),
        }


VideoPitanjeFormSet = inlineformset_factory(
    RadniNalog,
    VideoPitanje,
    form=VideoPitanjeForm,
    extra=1,
    can_delete=True,
)


###############################################################################
# 12) NOTIFIKACIJA, POVIJEST PROMJENA
###############################################################################
class NotifikacijaForm(BaseModelForm):
    class Meta:
        model = Notifikacija
        fields = [
            "korisnik",
            "poruka",
            "procitano",
            "datum_stvaranja",
            "prioritet",
            "tip",
        ]


class PovijestPromjenaForm(BaseModelForm):
    class Meta:
        model = PovijestPromjena
        fields = ["radni_nalog", "content_type", "object_id", "user", "promjene"]


###############################################################################
# 13) MJESEČNI WORK RECORD
###############################################################################
class MonthlyWorkRecordForm(BaseModelForm):
    class Meta:
        model = MonthlyWorkRecord
        fields = ["employee", "year", "month", "hours_worked"]


###############################################################################
# 14) PROIZVODNI RESURS
###############################################################################
class ProizvodniResursForm(BaseModelForm):
    """
    U finalnom modelu 'ProizvodniResurs' najčešće su polja: 'naziv', 'tip', 'opis',
    'dostupnost', 'kolicina', 'linked_sales_contract' i 'proizvodnja'.
    (Polje 'radni_nalog' je zamijenjeno s 'proizvodnja')
    """

    class Meta:
        model = ProizvodniResurs
        fields = [
            "naziv",
            "tip",
            "opis",
            "dostupnost",
            "kolicina",
            "linked_sales_contract",
            "proizvodnja",
        ]


###############################################################################
# 15) DODATNE FORME ZA "EVALUACIJA"
###############################################################################
class EvaluacijaRadnikaForm(BaseModelForm):
    class Meta:
        model = Employee
        fields = [
            "first_name",
            "last_name",
            "email",
            "employee_satisfaction",
            "satisfaction_score",
        ]


class EvaluacijaProjektaForm(BaseModelForm):
    class Meta:
        model = Projekt
        fields = ["naziv_projekta", "status", "pocetak_projekta", "rok_za_isporuku"]
        widgets = {
            "pocetak_projekta": forms.DateInput(attrs={"type": "date"}),
            "rok_za_isporuku": forms.DateInput(attrs={"type": "date"}),
        }


class EvaluacijaRadnogNalogaForm(BaseModelForm):
    class Meta:
        model = RadniNalog
        fields = ["naziv_naloga", "status", "datum_pocetka", "datum_zavrsetka"]
        widgets = {
            "datum_pocetka": forms.DateInput(attrs={"type": "date"}),
            "datum_zavrsetka": forms.DateInput(attrs={"type": "date"}),
        }


# Na kraju datoteke proizvodnja/forms.py dodajte sljedeći kod:

from django import forms
from django.utils.translation import gettext_lazy as _

from ljudski_resursi.models import Employee

from .models import Projekt


class CentralniPanelForm(forms.Form):
    project = forms.ModelChoiceField(
        queryset=Projekt.objects.filter(is_active=True),
        required=False,
        label=_("Projekt"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.filter(is_active=True),
        required=False,
        label=_("Zaposlenik"),
        widget=forms.Select(attrs={"class": "form-control"}),
    )
