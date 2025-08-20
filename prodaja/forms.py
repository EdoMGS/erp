from django import forms
from django.core.exceptions import ValidationError
from django.forms import ModelForm, inlineformset_factory

from .models import (
    FieldVisit,
    Quotation,
    SalesContract,
    SalesOpportunity,
    SalesOrder,
    TenderCost,
    TenderDocument,
    TenderLabor,
    TenderMaterial,
    TenderNeposredniTroskovi,
    TenderPosredniTroskovi,
    TenderPreparation,
    TenderRasclamba,
    WorkOrderInput,
)

# Osnovne forme


class OpportunityForm(ModelForm):
    class Meta:
        model = SalesOpportunity
        fields = "__all__"


class FieldVisitForm(ModelForm):
    class Meta:
        model = FieldVisit
        fields = [
            "opportunity",
            "visited_client",
            "date_of_visit",
            "purpose",
            "created_by",
        ]
        widgets = {
            "date_of_visit": forms.DateInput(attrs={"type": "date"}),
        }


class QuotationForm(ModelForm):
    class Meta:
        model = Quotation
        fields = "__all__"


class SalesOrderForm(ModelForm):
    class Meta:
        model = SalesOrder
        fields = "__all__"


class SalesContractForm(ModelForm):
    class Meta:
        model = SalesContract
        fields = "__all__"


class WorkOrderInputForm(ModelForm):
    class Meta:
        model = WorkOrderInput
        fields = ["radni_nalog", "proizvod", "kolicina", "cijena"]


# Tender Preparation – kompletna kalkulacija


class TenderDocumentForm(ModelForm):
    class Meta:
        model = TenderDocument
        fields = ["file", "description"]
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 3, "placeholder": "Unesite opis dokumenta..."}
            )
        }

    def clean_file(self):
        file = self.cleaned_data.get("file")
        if file:
            if file.size > 10 * 1024 * 1024:  # 10MB limit
                raise ValidationError("Datoteka ne smije biti veća od 10MB")
        return file


class TenderPreparationForm(ModelForm):
    class Meta:
        model = TenderPreparation
        fields = "__all__"
        widgets = {
            "delivery_opening_datetime": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "tender_validity": forms.DateInput(attrs={"type": "date"}),
            "evaluation_criteria": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Unesite kriterije evaluacije u JSON formatu",
                }
            ),
            "cashflow_plan": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Unesite plan cashflow-a u JSON formatu",
                }
            ),
            "nabava_updates": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Unesite ažurirane ponude materijala iz nabave u JSON formatu",
                }
            ),
            "required_documents": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "Unesite obaveznu dokumentaciju kao JSON",
                }
            ),
            "technical_specs": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Unesite tehničke specifikacije kao JSON",
                }
            ),
            "payment_schedule": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Unesite plan plaćanja kao JSON"}
            ),
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Dodatne napomene..."}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["opportunity"].queryset = SalesOpportunity.objects.filter(lead_source="tender")

    def clean(self):
        cleaned_data = super().clean()
        tender_validity = cleaned_data.get("tender_validity")
        opening_datetime = cleaned_data.get("delivery_opening_datetime")

        if tender_validity and opening_datetime and tender_validity < opening_datetime.date():
            raise ValidationError("Rok valjanosti ponude mora biti nakon datuma otvaranja ponuda")

        return cleaned_data


# Inline formsetovi

# Base formset settings
FORMSET_DEFAULTS = {
    "extra": 1,
    "can_delete": True,
    "can_order": True,
}

# Inline formsets with improved configuration
TenderDocumentFormSet = inlineformset_factory(
    TenderPreparation, TenderDocument, form=TenderDocumentForm, **FORMSET_DEFAULTS
)

TenderMaterialFormSet = inlineformset_factory(
    TenderPreparation,
    TenderMaterial,
    fields=("item_name", "unit_price", "quantity", "tax"),
    widgets={
        "item_name": forms.TextInput(attrs={"class": "form-control"}),
        "unit_price": forms.NumberInput(
            attrs={"class": "form-control", "min": "0", "step": "0.01"}
        ),
        "quantity": forms.NumberInput(attrs={"class": "form-control", "min": "1"}),
        "tax": forms.NumberInput(
            attrs={"class": "form-control", "min": "0", "max": "100", "step": "0.01"}
        ),
    },
    **FORMSET_DEFAULTS,
)

TenderLaborFormSet = inlineformset_factory(
    TenderPreparation,
    TenderLabor,
    fields=("labor_category", "hours", "hourly_rate"),
    extra=1,
    can_delete=True,
)

TenderCostFormSet = inlineformset_factory(
    TenderPreparation,
    TenderCost,
    fields=("cost_name", "cost_type", "amount"),
    extra=1,
    can_delete=True,
)

TenderRasclambaFormSet = inlineformset_factory(
    TenderPreparation,
    TenderRasclamba,
    fields=(
        "naziv_stavke",
        "sati_rada",
        "nas_materijal",
        "vanjska_usluga",
        "oprema_dijelovi",
        "dobavljac",
    ),
    extra=1,
    can_delete=True,
)

TenderNeposredniFormSet = inlineformset_factory(
    TenderPreparation,
    TenderNeposredniTroskovi,
    fields=("description", "monthly_cost", "project_cost", "coefficient"),
    extra=1,
    can_delete=True,
)

TenderPosredniFormSet = inlineformset_factory(
    TenderPreparation,
    TenderPosredniTroskovi,
    fields=("description", "monthly_cost", "project_cost"),
    extra=1,
    can_delete=True,
)


# Form validator mixins
class CostValidatorMixin:
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("amount", 0) < 0:
            raise ValidationError("Iznos ne može biti negativan")
        return cleaned_data


class TaxValidatorMixin:
    def clean_tax(self):
        tax = self.cleaned_data.get("tax")
        if tax and (tax < 0 or tax > 100):
            raise ValidationError("PDV mora biti između 0 i 100%")
        return tax
