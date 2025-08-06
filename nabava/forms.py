from django import forms
from django.utils.translation import gettext_lazy as _

from .models import (Dobavljac, GrupaDobavljaca, Narudzbenica,
                     NarudzbenicaStavka, ProcurementPlan, ProcurementRequest,
                     PurchaseOrder, PurchaseOrderLine)


class ProcurementPlanForm(forms.ModelForm):
    class Meta:
        model = ProcurementPlan
        fields = [
            "project_name",
            "item",
            "quantity",
            "required_date",
            "status",
            "responsible_person",
            "note",
        ]
        widgets = {
            "required_date": forms.DateInput(attrs={"type": "date"}),
            "note": forms.Textarea(attrs={"rows": 3}),
        }


class ProcurementRequestForm(forms.ModelForm):
    class Meta:
        model = ProcurementRequest
        fields = [
            "procurement_plan",
            "item",
            "quantity",
            "department",
            "status",
            "request_date",
        ]
        widgets = {"request_date": forms.DateInput(attrs={"type": "date"})}


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = [
            "supplier",
            "order_date",
            "expected_delivery_date",
            "status",
            "work_order",
            "is_jit",
            "delivery_schedule",
            "reference_price",
            "agreed_price",
            "justification_for_deviation",
        ]
        widgets = {
            "order_date": forms.DateInput(attrs={"type": "date"}),
            "expected_delivery_date": forms.DateInput(attrs={"type": "date"}),
            "delivery_schedule": forms.DateInput(attrs={"type": "date"}),
            "justification_for_deviation": forms.Textarea(attrs={"rows": 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        agreed_price = cleaned_data.get("agreed_price")
        reference_price = cleaned_data.get("reference_price")
        justification = cleaned_data.get("justification_for_deviation")

        if agreed_price and reference_price:
            if agreed_price > reference_price * 1.20 and not justification:
                raise forms.ValidationError(_("Potrebno je obrazloženje kada cijena prelazi referentnu za 20%"))
        return cleaned_data


class PurchaseOrderLineForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrderLine
        fields = ["artikl", "quantity", "unit_price", "discount"]
        widgets = {
            "discount": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "100"}),
        }

    def clean_quantity(self):
        quantity = self.cleaned_data.get("quantity")
        if quantity <= 0:
            raise forms.ValidationError(_("Količina mora biti veća od 0"))
        return quantity


class NarudzbenicaForm(forms.ModelForm):
    class Meta:
        model = Narudzbenica
        fields = ["broj", "datum", "dobavljac", "status"]
        widgets = {"datum": forms.DateInput(attrs={"type": "date"})}

    def clean_broj(self):
        broj = self.cleaned_data.get("broj")
        if Narudzbenica.objects.filter(broj=broj).exists():
            raise forms.ValidationError(_("Narudžbenica s ovim brojem već postoji"))
        return broj


class NarudzbenicaStavkaForm(forms.ModelForm):
    class Meta:
        model = NarudzbenicaStavka
        fields = ["artikl", "kolicina", "cijena"]

    def clean(self):
        cleaned_data = super().clean()
        kolicina = cleaned_data.get("kolicina")
        cijena = cleaned_data.get("cijena")

        if kolicina is not None and kolicina <= 0:
            raise forms.ValidationError(_("Količina mora biti veća od 0"))

        if cijena is not None and cijena < 0:
            raise forms.ValidationError(_("Cijena ne može biti negativna"))

        return cleaned_data

    def clean_artikl(self):
        artikl = self.cleaned_data.get("artikl")
        narudzbenica = self.instance.narudzbenica if self.instance else None

        if narudzbenica and NarudzbenicaStavka.objects.filter(narudzbenica=narudzbenica, artikl=artikl).exists():
            raise forms.ValidationError(_("Ovaj artikl je već dodan u narudžbenicu"))

        return artikl


class GrupaDobavljacaForm(forms.ModelForm):
    class Meta:
        model = GrupaDobavljaca
        fields = ["naziv", "opis", "is_active"]
        widgets = {
            "opis": forms.Textarea(attrs={"rows": 3}),
        }


class DobavljacForm(forms.ModelForm):
    class Meta:
        model = Dobavljac
        fields = [
            "naziv",
            "oib",
            "adresa",
            "grad",
            "drzava",
            "email",
            "telefon",
            "web",
            "grupa",
            "rejting",
            "rok_placanja",
            "popust",
            "is_active",
        ]
        widgets = {
            "rok_placanja": forms.NumberInput(attrs={"min": "0"}),
            "popust": forms.NumberInput(attrs={"step": "0.01", "min": "0", "max": "100"}),
        }

    def clean_oib(self):
        oib = self.cleaned_data.get("oib")
        if len(oib) != 11 or not oib.isdigit():
            raise forms.ValidationError(_("OIB mora sadržavati točno 11 brojeva"))
        return oib
