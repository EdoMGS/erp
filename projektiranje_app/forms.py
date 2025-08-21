from django import forms

from .models import DesignTask


###############################################################################
# 1) Bazna ModelForm
###############################################################################
class BaseModelForm(forms.ModelForm):
    """
    Zajednička poboljšanja i widgeti za sve forme u projektiranje_app.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _field_name, field in self.fields.items():  # noqa: B007
            # Ako widget već nema postavljenu klasu, dodaj 'form-control'
            if not field.widget.attrs.get("class"):
                field.widget.attrs["class"] = "form-control"

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data


###############################################################################
# 2) DESIGN TASK
###############################################################################
class DesignTaskForm(BaseModelForm):
    """Minimal form for stub DesignTask model (only 'placeholder' field)."""

    class Meta:
        model = DesignTask
        fields = ["placeholder"]
        widgets = {"placeholder": forms.TextInput(attrs={"class": "form-control"})}


###############################################################################
# All other legacy form classes removed in minimal stub state.
###############################################################################
