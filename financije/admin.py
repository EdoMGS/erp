from django.contrib import admin

from financije.models.taxconfig import Municipality

from .forms import (
    BankTransactionForm,
    BudgetForm,
    DebtForm,
    FinancialReportForm,
    InvoiceForm,
    MonthlyOverheadForm,
    OverheadForm,
    TaxConfigurationForm,
    VariablePayRuleForm,
)
from .models import Debt  # New models
from .models import (
    BankTransaction,
    Budget,
    CashFlow,
    FinancialDetails,
    FinancialReport,
    Invoice,
    MonthlyOverhead,
    Overhead,
    OverheadCategory,
    Salary,
    SalaryAddition,
    SalesContract,
    Tax,
    TaxConfiguration,
    VariablePayRule,
)

# financije/admin.py


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    form = InvoiceForm
    list_display = ["number", "client_name", "total_amount", "issue_date", "status"]
    list_filter = ["status", "issue_date"]
    search_fields = ["number", "client_name"]
    date_hierarchy = "issue_date"


@admin.register(FinancialDetails)
class FinancialDetailsAdmin(admin.ModelAdmin):
    list_display = (
        "total_price",
        "contracted_net_price",
        "contracted_gross_price",
        "actual_costs",
    )
    search_fields = ("contracted_net_price",)
    list_filter = ("contracted_net_price",)
    ordering = ("-contracted_net_price",)


@admin.register(TaxConfiguration)
class TaxConfigurationAdmin(admin.ModelAdmin):
    form = TaxConfigurationForm
    list_display = ("name", "tax_rate", "opis")  # prilagodite poljima koja postoje
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(VariablePayRule)
class VariablePayRuleAdmin(admin.ModelAdmin):
    form = VariablePayRuleForm
    list_display = ("position", "expertise_level", "variable_pay", "bonus")
    search_fields = ("position__title", "expertise_level__name")
    list_filter = ("position", "expertise_level")
    ordering = ("position", "expertise_level")


@admin.register(Overhead)
class OverheadAdmin(admin.ModelAdmin):
    form = OverheadForm
    list_display = ("godina", "mjesec", "overhead_ukupno", "mjesecni_kapacitet_sati")
    search_fields = ("godina", "mjesec")
    list_filter = ("godina", "mjesec")
    ordering = ("-godina", "-mjesec")


@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ("name", "tax_rate")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Salary)
class SalaryAdmin(admin.ModelAdmin):
    list_display = ("employee", "gross_amount", "taxes", "net_amount", "date")
    search_fields = ("employee__name",)
    list_filter = ("employee", "date")
    ordering = ("employee",)


@admin.register(Tax)
class TaxAdmin(admin.ModelAdmin):
    list_display = ("name", "rate")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(SalaryAddition)
class SalaryAdditionAdmin(admin.ModelAdmin):
    list_display = ("salary", "name", "amount")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(CashFlow)
class CashFlowAdmin(admin.ModelAdmin):
    list_display = ("datum", "iznos", "opis", "tip_transakcije")
    search_fields = ("datum", "opis")
    list_filter = ("tip_transakcije", "datum")
    ordering = ("-datum",)


@admin.register(FinancialReport)
class FinancialReportAdmin(admin.ModelAdmin):
    form = FinancialReportForm
    list_display = (
        "period",
        "year",
        "month",
        "kvartal",
        "priljev_ukupno",
        "odljev_ukupno",
        "neto_cash_flow",
    )
    search_fields = ("period", "year", "month", "kvartal")
    list_filter = ("period", "year", "month", "kvartal")
    ordering = ("-year", "-month")


@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    form = DebtForm
    list_display = (
        "client_name",
        "invoice",
        "due_date",
        "amount_due",
        "is_paid",
        "days_overdue",
    )
    search_fields = ("client_name", "invoice__number")
    list_filter = ("is_paid", "due_date")
    ordering = ("-due_date",)


@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    form = BankTransactionForm
    list_display = ("referenca", "tip_transakcije", "iznos", "datum", "saldo")
    search_fields = ("referenca", "opis")
    list_filter = ("tip_transakcije", "datum")
    ordering = ("-datum",)


@admin.register(OverheadCategory)
class OverheadCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(MonthlyOverhead)
class MonthlyOverheadAdmin(admin.ModelAdmin):
    form = MonthlyOverheadForm
    list_display = ("year", "month", "category", "amount")
    search_fields = ("year", "month", "category__name")
    list_filter = ("year", "month", "category")
    ordering = ("-year", "-month")


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    form = BudgetForm
    list_display = (
        "godina",
        "mjesec",
        "predvidjeni_prihod",
        "predvidjeni_trosak",
        "stvarni_prihod",
        "stvarni_trosak",
    )
    search_fields = ("godina", "mjesec")
    list_filter = ("godina", "mjesec")
    ordering = ("-godina", "-mjesec")


@admin.register(SalesContract)
class SalesContractAdmin(admin.ModelAdmin):
    list_display = ("contract_number", "client_name")
    search_fields = ("contract_number", "client_name")
    list_filter = ()  # No client FK available in MVP


# --- New Local Tax Rate admin registration ---
try:
    from financije.models.tax_local_rate import TaxLocalRate

    @admin.register(TaxLocalRate)
    class TaxLocalRateAdmin(admin.ModelAdmin):
        list_display = (
            "tenant",
            "jls_code",
            "name",
            "lower_rate",
            "higher_rate",
            "valid_from",
            "valid_to",
            "active",
        )
        list_filter = ("tenant", "jls_code", "active")
        search_fields = ("jls_code", "name")
except Exception:  # pragma: no cover - model may not be migrated yet in some contexts
    pass
