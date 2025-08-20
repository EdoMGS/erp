from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserChangeForm, UserCreationForm

from .models import (
    Department,
    Employee,
    ExpertiseLevel,
    HierarchicalLevel,
    Position,
    RadnaEvaluacija,
)


class BaseModelForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for _field_name, field in self.fields.items():  # noqa: B007
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} form-control".strip()


class DepartmentForm(BaseModelForm):
    class Meta:
        model = Department
        fields = "__all__"

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if Department.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Department with this name already exists.")
        return name


class ExpertiseLevelForm(BaseModelForm):
    class Meta:
        model = ExpertiseLevel
        fields = ["name", "description"]

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if ExpertiseLevel.objects.filter(name__iexact=name).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Expertise Level with this name already exists.")
        return name


class HierarchicalLevelForm(BaseModelForm):
    class Meta:
        model = HierarchicalLevel
        fields = ["name", "level", "description"]

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if (
            HierarchicalLevel.objects.filter(name__iexact=name)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("Hierarchical Level with this name already exists.")
        return name

    def clean_level(self):
        level = self.cleaned_data.get("level")
        if HierarchicalLevel.objects.filter(level=level).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Hierarchical Level with this level already exists.")
        return level


class EmployeeForm(BaseModelForm):
    class Meta:
        model = Employee
        fields = "__all__"
        widgets = {
            "first_name": forms.TextInput(
                attrs={"placeholder": "Enter first name...", "class": "form-control"}
            ),
            "last_name": forms.TextInput(
                attrs={"placeholder": "Enter last name...", "class": "form-control"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "Enter email...", "class": "form-control"}
            ),
            "position": forms.Select(attrs={"class": "form-select"}),
            "salary_coefficient": forms.NumberInput(attrs={"step": 0.1, "class": "form-control"}),
            "expertise_level": forms.Select(attrs={"class": "form-select"}),
            "department": forms.Select(attrs={"class": "form-select"}),
            "manager": forms.Select(attrs={"class": "form-select"}),
        }

    expertise_level = forms.ModelChoiceField(
        queryset=ExpertiseLevel.objects.all(),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and not email.endswith("@mgs-grupa.com"):
            raise forms.ValidationError("Email must be @mgs-grupa.com domain.")
        if (
            email
            and Employee.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists()
        ):
            self.add_error("email", "Email already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        user = self.instance.user if hasattr(self.instance, "user") else None
        if user:
            # ...existing validations...
            pass
        return cleaned_data


class PositionForm(BaseModelForm):
    class Meta:
        model = Position
        fields = "__all__"

    def clean_title(self):
        title = self.cleaned_data.get("title")
        if Position.objects.filter(title__iexact=title).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Position with this title already exists.")
        return title


class RadnaEvaluacijaForm(forms.ModelForm):
    class Meta:
        model = RadnaEvaluacija
        fields = "__all__"


class OnboardingForm(forms.Form):
    employee = forms.ModelChoiceField(queryset=Employee.objects.all())
    start_date = forms.DateField()


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "email", "password1", "password2"]


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = get_user_model()
        fields = ["username", "email", "first_name", "last_name"]
