import re

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Layout, Row, Submit
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from common.validators import validate_oib
from prodaja.models import SalesOpportunity

from .models import CityPostalCode, ClientActivityLog, ClientSupplier


class ClientSupplierForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"

        self.helper.layout = Layout(
            Row(
                Column("name", css_class="form-group col-md-6"),
                Column("email", css_class="form-group col-md-6"),
            ),
            Row(
                Column("phone", css_class="form-group col-md-6"),
                Column("oib", css_class="form-group col-md-6"),
            ),
            Row(
                Column("address", css_class="form-group col-md-12"),
            ),
            Row(
                Column("country", css_class="form-group col-md-4"),
                Column("city", css_class="form-group col-md-4"),
                Column("postal_code", css_class="form-group col-md-4"),
            ),
            Row(
                Column("county", css_class="form-group col-md-4"),
                Column("relationship_status", css_class="form-group col-md-4"),
                Column("is_active", css_class="form-group col-md-4"),
            ),
            Row(
                Column("long_term_relationship", css_class="form-group col-md-12"),
            ),
            Submit("submit", _("Spremi"), css_class="btn btn-primary"),
        )

    class Meta:
        model = ClientSupplier
        fields = [
            "name",
            "email",
            "phone",
            "oib",
            "address",
            "city",
            "postal_code",
            "county",
            "country",
            "relationship_status",
            "is_active",
            "long_term_relationship",
        ]
        labels = {
            "name": "Naziv",
            "address": "Adresa",
            "email": "E-mail",
            "phone": "Telefon",
            "is_active": "Aktivan",
            "oib": "OIB",
            "country": "Država",
            "city": "Grad",
            "postal_code": "Poštanski broj",
            "county": "Županija",
        }

    def clean(self):
        cleaned_data = super().clean()
        postal_code = cleaned_data.get("postal_code")
        city = cleaned_data.get("city")

        if postal_code or city:
            city_postal = None
            if postal_code:
                city_postal = CityPostalCode.objects.filter(postal_code=postal_code).first()
                if city_postal and city and city_postal.city != city:
                    self.add_error(None, _("Uneseni grad ne odgovara poštanskom broju"))
                elif city_postal:
                    cleaned_data["city"] = city_postal.city
                    cleaned_data["county"] = city_postal.county
            elif city:
                city_postal = CityPostalCode.objects.filter(city=city).first()
                if city_postal:
                    cleaned_data["postal_code"] = city_postal.postal_code
                    cleaned_data["county"] = city_postal.county

            if not city_postal:
                self.add_error("postal_code", _("Nevažeći poštanski broj ili grad"))

        return cleaned_data

    def clean_oib(self):
        oib = self.cleaned_data.get("oib")
        validate_oib(oib)
        return oib

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and not re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email):
            raise ValidationError("Enter a valid email address.")
        return email

    def clean_relationship_status(self):
        status = self.cleaned_data.get("relationship_status")
        is_active = self.cleaned_data.get("is_active")

        if status == "active" and not is_active:
            raise ValidationError(_("Klijent ne može imati aktivan status ako nije aktivan"))
        return status


class ClientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Submit"))

    class Meta:
        model = ClientSupplier
        fields = ["name", "address", "email", "phone", "is_active", "oib"]
        labels = {
            "name": "Naziv",
            "address": "Adresa",
            "email": "E-mail",
            "phone": "Telefon",
            "is_active": "Aktivan",
            "oib": "OIB",
        }


class ClientActivityLogForm(forms.ModelForm):
    class Meta:
        model = ClientActivityLog
        fields = ["client", "activity", "activity_type"]
        widgets = {
            "activity": forms.Textarea(attrs={"rows": 3}),
            "activity_type": forms.HiddenInput(),  # Hide activity_type if it's set programmatically
        }

    def __init__(self, *args, activity_type="other", **kwargs):
        super().__init__(*args, **kwargs)
        if activity_type:
            self.initial["activity_type"] = activity_type


class SalesOpportunityForm(forms.ModelForm):
    """Form for creating/editing sales opportunities"""

    class Meta:
        model = SalesOpportunity
        fields = [
            "name",
            "client",
            "stage",
            "budget",
            "lead_source",
            "project_service_type",
            "authority",
            "need",
            "timeframe",
            "assigned_to",
            "public_tender_number",
        ]
        labels = {
            "name": _("Naziv prilike"),
            "client": _("Klijent"),
            "stage": _("Status"),
            "budget": _("Budžet"),
            "lead_source": _("Izvor prilike"),
            "project_service_type": _("Vrsta projekta/usluge"),
            "authority": _("Ovlasti za potpis"),
            "need": _("Jasna potreba"),
            "timeframe": _("Vremenski okvir"),
            "assigned_to": _("Odgovorna osoba"),
            "public_tender_number": _("Broj javnog natječaja"),
        }
