# skladiste/forms.py

from django import forms

from .models import (
    Alat,
    Artikl,
    DnevnikDogadaja,
    HTZOprema,
    Izdatnica,
    IzdatnicaStavka,
    Lokacija,
    Materijal,
    Primka,
    PrimkaStavka,
    SkladisteResurs,
    Zona,
)


###############################################################################
# BAZNA FORMA ZA STIL
###############################################################################
class BaseSkladisteForm(forms.ModelForm):
    """
    Zajednička poboljšanja i widgeti za sve forme u 'skladiste' app.
    - Dodaj 'form-control' klasu za bootstrap styling
    - Mjesto za zajedničku clean() logiku
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean(self):
        cleaned_data = super().clean()
        # Možeš ovdje dodati zajedničku validaciju
        return cleaned_data


###############################################################################
# 1) FORME ZA ZONU I LOKACIJU
###############################################################################
class ZonaForm(BaseSkladisteForm):
    class Meta:
        model = Zona
        fields = ["naziv", "opis"]


class LokacijaForm(BaseSkladisteForm):
    class Meta:
        model = Lokacija
        fields = ["naziv", "opis", "zona"]


###############################################################################
# 2) ARTIKL, ZALIHA, SKLADIŠNI RESURS
###############################################################################
class ArtiklForm(BaseSkladisteForm):
    class Meta:
        model = Artikl
        fields = "__all__"


class SkladisteResursForm(BaseSkladisteForm):
    class Meta:
        model = SkladisteResurs
        fields = [
            "naziv",
            "opis",
            "kolicina",
            "lokacija",
        ]


###############################################################################
# 3) MATERIJAL I INVENTORY
###############################################################################
class MaterijalForm(BaseSkladisteForm):
    """Materijal (vezan na RadniNalog iz 'proizvodnja')."""

    class Meta:
        model = Materijal
        exclude = ["tehnicki_nacrt"]  # Exclude this field from form to avoid circular import
        # Or specify only the fields you want to include:

    # fields = [
    #     'artikl', 'radni_nalog', 'status', 'naziv', 'cijena',
    #     'kolicina', 'opis', 'datum_dostave'
    # ]


# class InventoryItemForm(BaseSkladisteForm):
#     """
#     Evidencija 'Materijal + količina + lokacija (tekst)'
#     - Ako radiš klasičan popis stanja u skladištu.
#     """
#     class Meta:
#         model = InventoryItem
#         fields = [
#             "materijal",
#             "quantity",
#             "location",
#         ]
#         # last_updated je auto_now, ne ide u formu


###############################################################################
# 4) ALAT I HTZ OPREMA
###############################################################################
class AlatForm(BaseSkladisteForm):
    class Meta:
        model = Alat
        fields = [
            "naziv",
            "inventarski_broj",
            "zaduzen",
            "is_assigned",
            "assigned_to",
        ]


class HTZOpremaForm(BaseSkladisteForm):
    class Meta:
        model = HTZOprema
        fields = [
            "vrsta",
            "stanje",
            "is_assigned",
            "htz_equipment_tracking",
            "assigned_to",
        ]


###############################################################################
# 5) DNEVNIK DOGAĐAJA
###############################################################################
class DnevnikDogadajaForm(BaseSkladisteForm):
    class Meta:
        model = DnevnikDogadaja
        fields = [
            "dogadaj",
            "artikl",
        ]
        # datum je auto_now_add, ne ide u form


###############################################################################
# 6) PRIMKA I IZDATNICA
###############################################################################
class PrimkaForm(BaseSkladisteForm):
    class Meta:
        model = Primka
        fields = ["broj_primke", "datum", "dobavljac", "napomena"]
        widgets = {
            "datum": forms.DateInput(attrs={"type": "date"}),
        }


class PrimkaStavkaForm(BaseSkladisteForm):
    class Meta:
        model = PrimkaStavka
        fields = ["artikl", "kolicina", "cijena"]


class IzdatnicaForm(BaseSkladisteForm):
    class Meta:
        model = Izdatnica
        fields = ["broj_izdatnice", "datum", "preuzeo", "napomena"]
        widgets = {
            "datum": forms.DateInput(attrs={"type": "date"}),
        }


class IzdatnicaStavkaForm(BaseSkladisteForm):
    class Meta:
        model = IzdatnicaStavka
        fields = ["artikl", "kolicina"]


###############################################################################
# INLINE FORMSETS (PO TREBI)
###############################################################################
"""
Ako trebaš inline formset, npr. InventoryItem unutar Materijala ili sl., 
možeš definirati inline formset-ove ovdje.

Primjer (ako želiš dodavati InventoryItem unutar Materijala):
"""

# from django.forms import inlineformset_factory

# InventoryItemFormSet = inlineformset_factory(
#     parent_model=Materijal,
#     model=InventoryItem,
#     form=InventoryItemForm,
#     fields=['quantity', 'location'],
#     extra=1,
#     can_delete=True
# )
