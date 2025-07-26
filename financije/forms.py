# financije/forms.py

from django import forms
from django.apps import apps  # Added import for apps
from django.utils.translation import \
    gettext_lazy as _  # Added import for translation function

from client_app.models import ClientSupplier  # Changed: import from client_app

from .models import (BankTransaction, Budget, CashFlow, Debt, FinancialDetails,
                     FinancialReport, Invoice, InvoiceLine, MonthlyOverhead,
                     Municipality, Overhead, OverheadCategory, Payment, Salary,
                     SalaryAddition, SalesContract, Tax, TaxConfiguration,
                     VariablePayRule)


#############################################
# 1) BaseModelForm (za zajedničke widgete)
#############################################
class BaseModelForm(forms.ModelForm):
    """
    Ako želite svim poljima dodati 'form-control', možete to učiniti ovako.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get("class", "")
            field.widget.attrs["class"] = f"{existing_classes} form-control".strip()


#############################################
# 2) Invoice Form
#############################################
class InvoiceForm(BaseModelForm):
    class Meta:
        model = Invoice
        fields = [
            "client",
            "invoice_number",
            "issue_date",
            "due_date",
            "pdv_rate",
            "payment_method",
            "status_fakture",
            "user",
            "is_guaranteed",
            "guarantee_details",
            "financial_guarantee",
            "tender_statement",
            "public_tender_ref",
        ]
        widgets = {
            "client": forms.Select(attrs={"class": "form-select"}),
            "invoice_number": forms.TextInput(),
            "issue_date": forms.DateInput(attrs={"type": "date"}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
            "pdv_rate": forms.NumberInput(),
            "payment_method": forms.Select(attrs={"class": "form-select"}),
            "status_fakture": forms.Select(attrs={"class": "form-select"}),
            "user": forms.Select(),
            "is_guaranteed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "guarantee_details": forms.Textarea(),
            "financial_guarantee": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "tender_statement": forms.Textarea(),
            "public_tender_ref": forms.TextInput(),
        }


#############################################
# 3) FinancialDetails Form
#############################################
class FinancialDetailsForm(BaseModelForm):
    class Meta:
        model = FinancialDetails
        fields = [
            "total_price",
            "contracted_net_price",
            "vat_rate",
            "contracted_gross_price",
            "predicted_costs",
            "actual_costs",
            "predicted_profit",
            "actual_profit",
        ]
        widgets = {
            "total_price": forms.NumberInput(),
            "contracted_net_price": forms.NumberInput(),
            "vat_rate": forms.NumberInput(),
            "contracted_gross_price": forms.NumberInput(),
            "predicted_costs": forms.NumberInput(),
            "actual_costs": forms.NumberInput(),
            "predicted_profit": forms.NumberInput(),
            "actual_profit": forms.NumberInput(),
        }


#############################################
# 4) TaxConfiguration Form
#############################################
class TaxConfigurationForm(BaseModelForm):
    class Meta:
        model = TaxConfiguration
        fields = "__all__"
        widgets = {
            "name": forms.TextInput(),
            "tax_rate": forms.NumberInput(),
            "opis": forms.Textarea(),  # ako koristite polje 'opis'
            "mirovinsko_1": forms.NumberInput(),
            "mirovinsko_2": forms.NumberInput(),
            "zdravstveno": forms.NumberInput(),
            "niza_stopa": forms.NumberInput(),
            "visa_stopa": forms.NumberInput(),
            "osobni_odbitak": forms.NumberInput(),
            "prirez": forms.NumberInput(),
            "granica_visa_stopa": forms.NumberInput(),
            "minimal_salary": forms.NumberInput(),
        }


#############################################
# 5) VariablePayRule Form
#############################################
class VariablePayRuleForm(BaseModelForm):
    class Meta:
        model = VariablePayRule
        fields = "__all__"
        widgets = {
            "position": forms.Select(attrs={"class": "form-select"}),
            "expertise_level": forms.Select(attrs={"class": "form-select"}),
            "variable_pay": forms.NumberInput(),
            "bonus": forms.NumberInput(),
        }


#############################################
# 6) Overhead Form
#############################################
class OverheadForm(forms.ModelForm):
    class Meta:
        model = Overhead
        fields = "__all__"
        widgets = {
            "godina": forms.NumberInput(),
            "mjesec": forms.NumberInput(),
            "overhead_ukupno": forms.NumberInput(),
            "mjesecni_kapacitet_sati": forms.NumberInput(),
        }


#############################################
# 7) ClientSupplier Form
#############################################
class ClientSupplierForm(forms.ModelForm):
    class Meta:
        model = ClientSupplier
        fields = "__all__"


#############################################
# 8) Municipality Form
#############################################
class MunicipalityForm(forms.ModelForm):
    class Meta:
        model = Municipality
        fields = "__all__"


#############################################
# 9) Salary Form
#############################################
class SalaryForm(forms.ModelForm):
    class Meta:
        model = Salary
        fields = "__all__"


#############################################
# 10) Tax Form
#############################################
class TaxForm(forms.ModelForm):
    class Meta:
        model = Tax
        fields = "__all__"


#############################################
# 11) SalaryAddition Form
#############################################
class SalaryAdditionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Lazy load related models
        RadnaEvaluacija = apps.get_model("ljudski_resursi", "RadnaEvaluacija")
        OcjenaKvalitete = apps.get_model("ljudski_resursi", "OcjenaKvalitete")

        self.fields["evaluation"] = forms.ModelChoiceField(
            queryset=RadnaEvaluacija.objects.all(),
            required=False,
            label=_("Evaluacija"),
        )
        self.fields["quality_score"] = forms.ModelChoiceField(
            queryset=OcjenaKvalitete.objects.all(),
            required=False,
            label=_("Ocjena Kvalitete"),
        )

    class Meta:
        model = SalaryAddition
        fields = [
            "salary",
            "name",
            "amount",
            "type",
            "evaluation",
            # Remove quality_score from fields list since we're handling it in __init__
        ]
        widgets = {
            "salary": forms.Select(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "amount": forms.NumberInput(attrs={"class": "form-control"}),
            "type": forms.Select(attrs={"class": "form-control"}),
        }


#############################################
# 12) Payment Form (ako ga imate)
#############################################
class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = "__all__"


#############################################
# 13) CashFlow Form
#############################################
class CashFlowForm(forms.ModelForm):
    class Meta:
        model = CashFlow
        fields = "__all__"


#############################################
# 14) FinancialReport Form
#############################################
class FinancialReportForm(BaseModelForm):
    class Meta:
        model = FinancialReport
        fields = "__all__"
        widgets = {
            "period": forms.Select(attrs={"class": "form-select"}),
            "year": forms.NumberInput(),
            "month": forms.NumberInput(),
            "kvartal": forms.NumberInput(),
            "priljev_ukupno": forms.NumberInput(),
            "odljev_ukupno": forms.NumberInput(),
            "neto_cash_flow": forms.NumberInput(),
        }


#############################################
# 15) Debt Form
#############################################
class DebtForm(forms.ModelForm):
    class Meta:
        model = Debt
        fields = "__all__"


#############################################
# 16) BankTransaction Form
#############################################
class BankTransactionForm(forms.ModelForm):
    class Meta:
        model = BankTransaction
        fields = "__all__"
        widgets = {
            "tip_transakcije": forms.Select(attrs={"class": "form-select"}),
            "iznos": forms.NumberInput(),
            "opis": forms.TextInput(),
            "datum": forms.DateInput(attrs={"type": "date"}),
            "referenca": forms.TextInput(),
            "saldo": forms.NumberInput(),
        }


#############################################
# 17) OverheadCategory Form
#############################################
class OverheadCategoryForm(forms.ModelForm):
    class Meta:
        model = OverheadCategory
        fields = "__all__"


#############################################
# 18) MonthlyOverhead Form
#############################################
class MonthlyOverheadForm(forms.ModelForm):
    class Meta:
        model = MonthlyOverhead
        fields = "__all__"
        widgets = {
            "year": forms.NumberInput(),
            "month": forms.NumberInput(),
            "category": forms.Select(attrs={"class": "form-select"}),
            "amount": forms.NumberInput(),
        }


#############################################
# 19) Budget Form
#############################################
class BudgetForm(forms.ModelForm):
    class Meta:
        model = Budget
        fields = "__all__"
        widgets = {
            "godina": forms.NumberInput(),
            "mjesec": forms.NumberInput(),
            "predvidjeni_prihod": forms.NumberInput(),
            "predvidjeni_trosak": forms.NumberInput(),
            "stvarni_prihod": forms.NumberInput(),
            "stvarni_trosak": forms.NumberInput(),
        }


#############################################
# 20) SalesContract Form
#############################################
class SalesContractForm(forms.ModelForm):
    class Meta:
        model = SalesContract
        fields = "__all__"
        widgets = {
            "contract_number": forms.TextInput(),
            "client": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "public_tender_number": forms.TextInput(),
            "bank_guarantee_required": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "total_amount": forms.NumberInput(),
            "discount": forms.NumberInput(),
            "sales_order": forms.Select(attrs={"class": "form-select"}),
            "delivery_schedule": forms.Textarea(),
            "client_specific_reqs": forms.Textarea(),
            "related_production_order": forms.Select(attrs={"class": "form-select"}),
        }


#############################################
# 21) InvoiceLine Form
#############################################
class InvoiceLineForm(forms.ModelForm):
    """Form for invoice line items"""

    class Meta:
        model = InvoiceLine
        fields = ["description", "quantity", "unit_price", "tax_rate"]
        widgets = {
            "description": forms.TextInput(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "unit_price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "tax_rate": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }
