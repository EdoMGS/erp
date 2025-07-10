from decimal import Decimal

from django import forms
from django.utils.translation import gettext_lazy as _

from .models import (BillOfMaterials, BOMItem, CADDocument, DesignRevision,
                     DesignSegment, DesignTask, DynamicPlan)


###############################################################################
# 1) Bazna ModelForm
###############################################################################
class BaseModelForm(forms.ModelForm):
    """
    Zajednička poboljšanja i widgeti za sve forme u projektiranje_app.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            # Ako widget već nema postavljenu klasu, dodaj 'form-control'
            if not field.widget.attrs.get('class'):
                field.widget.attrs['class'] = 'form-control'

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


###############################################################################
# 2) DESIGN TASK
###############################################################################
class DesignTaskForm(BaseModelForm):
    class Meta:
        model = DesignTask
        # Audit polja ne želimo mijenjati ručno
        exclude = ('created_at', 'updated_at',)
        widgets = {
            'projekt': forms.Select(attrs={'class': 'form-select'}),
            'projektant': forms.Select(attrs={'class': 'form-select'}),
            'tip_vozila': forms.Select(attrs={'class': 'form-select'}),
            'predvidjeni_sati_dizajna': forms.NumberInput(),
            'utroseni_sati': forms.NumberInput(),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'datum_pocetka': forms.DateInput(attrs={'type': 'date'}),
            'datum_zavrsetka': forms.DateInput(attrs={'type': 'date'}),
            'napomena': forms.Textarea(),
            'solidworks_drawing': forms.ClearableFileInput(),
            'autocad_drawing': forms.ClearableFileInput(),
        }


###############################################################################
# 3) DESIGN SEGMENT
###############################################################################
class DesignSegmentForm(BaseModelForm):
    class Meta:
        model = DesignSegment
        # Korisniku su potrebna samo osnovna polja za segment
        fields = ['design_task', 'segment_type', 'opis', 'planirani_sati', 'utroseni_sati']
        widgets = {
            'design_task': forms.Select(attrs={'class': 'form-select'}),
            'segment_type': forms.Select(attrs={'class': 'form-select'}),
            'opis': forms.Textarea(),
            'planirani_sati': forms.NumberInput(),
            'utroseni_sati': forms.NumberInput(),
        }


###############################################################################
# 4) DYNAMIC PLAN
###############################################################################
class DynamicPlanForm(BaseModelForm):
    class Meta:
        model = DynamicPlan
        # updated_at se automatski postavlja, pa ga izuzimamo
        exclude = ('updated_at',)
        widgets = {
            'design_task': forms.Select(attrs={'class': 'form-select'}),
            'design_segment': forms.Select(attrs={'class': 'form-select'}),
            'json_data': forms.Textarea(attrs={'rows': 4}),
            'pocetak_plana': forms.DateInput(attrs={'type': 'date'}),
            'kraj_plana': forms.DateInput(attrs={'type': 'date'}),
            'napomena': forms.Textarea(),
        }


###############################################################################
# 5) BILL OF MATERIALS
###############################################################################
class BillOfMaterialsForm(BaseModelForm):
    class Meta:
        model = BillOfMaterials
        exclude = ('created_at', 'updated_at',)
        widgets = {
            'design_task': forms.Select(attrs={'class': 'form-select'}),
            'design_segment': forms.Select(attrs={'class': 'form-select'}),
            'naziv': forms.TextInput(),
            'opis': forms.Textarea(),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }


###############################################################################
# 6) BOM ITEM
###############################################################################
class BOMItemForm(BaseModelForm):
    class Meta:
        model = BOMItem
        fields = ['bom', 'materijal', 'kolicina', 'napomena']
        widgets = {
            'bom': forms.Select(attrs={'class': 'form-select'}),
            'materijal': forms.Select(attrs={'class': 'form-select'}),
            'kolicina': forms.NumberInput(),
            'napomena': forms.TextInput(),
        }


###############################################################################
# 7) CAD DOCUMENT
###############################################################################
class CADDocumentForm(BaseModelForm):
    class Meta:
        model = CADDocument
        exclude = ('uploaded_at',)
        widgets = {
            'design_task': forms.Select(attrs={'class': 'form-select'}),
            'design_segment': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.ClearableFileInput(),
            'file_type': forms.Select(attrs={'class': 'form-select'}),
        }


###############################################################################
# 8) DESIGN REVISION
###############################################################################
class DesignRevisionForm(BaseModelForm):
    class Meta:
        model = DesignRevision
        exclude = ('created_at',)
        widgets = {
            'design_task': forms.Select(attrs={'class': 'form-select'}),
            'design_segment': forms.Select(attrs={'class': 'form-select'}),
            'broj_revizije': forms.NumberInput(),
            'opis': forms.Textarea(),
            'autor': forms.Select(attrs={'class': 'form-select'}),
        }
