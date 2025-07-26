from django import forms

from .models import LabourEntry


class LabourEntryForm(forms.ModelForm):
    class Meta:
        model = LabourEntry
        fields = ["project", "hours", "date"]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user:
            self.instance.worker = user
        self.fields["date"].widget.attrs["type"] = "date"
