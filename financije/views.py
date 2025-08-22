from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,  # Dodali UpdateView
    ListView,
    UpdateView,
    View,
)

# Dodajemo REST framework imports
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .forms import BudgetForm, InvoiceForm, OverheadForm
from .models import (
    AuditLog,
    BankTransaction,
    Budget,
    CashFlow,
    Debt,
    FinancialReport,
    Invoice,
    MonthlyOverhead,
    Overhead,
    OverheadCategory,
    Salary,
    SalaryAddition,
    Tax,
    TaxConfiguration,
    VariablePayRule,
)
from .reports import general_ledger, trial_balance

# Add serializer imports
from .serializers import (
    AuditLogSerializer,
    BankTransactionSerializer,  # Dodano
    BudgetSerializer,  # Dodano
    DebtSerializer,  # Dodano
    FinancialReportSerializer,  # Dodano
    InvoiceSerializer,
    MonthlyOverheadSerializer,  # Dodano
    OverheadCategorySerializer,  # Dodano
    SalaryAdditionSerializer,  # Dodano
    SalarySerializer,  # Dodano
    TaxConfigurationSerializer,  # Dodano
    TaxSerializer,  # Dodano
    VariablePayRuleSerializer,  # Dodano
)

# ...existing code...


def home(request):
    return render(request, "financije/home.html")


@login_required
def invoice_form(request, pk=None):
    InvoiceModel = apps.get_model("financije", "Invoice")  # da izbjegnemo eventualne petlje
    invoice = get_object_or_404(InvoiceModel, pk=pk) if pk else None

    if request.method == "POST":
        return handle_invoice_post(request, invoice)

    form = InvoiceForm(instance=invoice)
    return render(request, "financije/invoice_form.html", {"form": form})


def handle_invoice_post(request, invoice):
    form = InvoiceForm(request.POST, instance=invoice)
    if form.is_valid():
        try:
            form.save()
            return redirect("invoice_list")
        except Exception as e:
            form.add_error(None, f"An error occurred while saving the form: {e}")
    return render(request, "financije/invoice_form.html", {"form": form})


@login_required
def create_invoice_from_quote(request, quote_id):
    Quote = apps.get_model("production", "Quote")
    quote = get_object_or_404(Quote, pk=quote_id)
    initial_data = {
        "client": quote.client_id,  # ili .client ako je FK objekt
        "amount": quote.amount,
        # Dodajte ostala polja po potrebi
    }
    form = InvoiceForm(initial=initial_data)

    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("invoice_list")

    return render(request, "financije/invoice_form.html", {"form": form})


def view_invoices(request):
    InvoiceModel = apps.get_model("financije", "Invoice")
    invoices = InvoiceModel.objects.all()
    return render(request, "financije/view_invoices.html", {"invoices": invoices})


@login_required
def generate_payment_order(request, invoice_id):
    InvoiceModel = apps.get_model("financije", "Invoice")
    invoice = get_object_or_404(InvoiceModel, pk=invoice_id)

    # Ako je polje u modelu 'status_fakture', koristimo ga:
    # if invoice.status_fakture == 'odobreno':
    #     ...

    # Ako je pak 'status_invoice' (ili 'approved'), podesite prema stvarnoj shemi:
    if hasattr(invoice, "status_fakture") and invoice.status_fakture == "odobreno":
        # Generiraj payment order
        print(f"Payment order generated for invoice: {invoice.invoice_number}")

        # Pošalji email
        send_mail(
            "Payment Order Generated",
            f"A payment order for invoice {invoice.invoice_number} has been generated.",
            "no-reply@erp-system.com",
            [invoice.client.email],
        )

        # Log
        AuditLog.objects.create(
            user=request.user,
            action="Generated payment order",
            model_name="Invoice",
            instance_id=invoice_id,
        )

    return redirect("view_invoices")


@login_required
def delete_invoice(request, pk):
    InvoiceModel = apps.get_model("financije", "Invoice")
    invoice = get_object_or_404(InvoiceModel, pk=pk)
    invoice.delete()

    # Log the deletion action
    AuditLog.objects.create(
        user=request.user,
        action="Deleted invoice",
        model_name="Invoice",
        instance_id=pk,
    )

    return redirect("view_invoices")


@login_required
def view_salaries(request):
    SalaryModel = apps.get_model("financije", "Salary")
    salaries = SalaryModel.objects.all().select_related("employee")
    # Dodaj logiku izračuna ako je potrebno
    for salary in salaries:
        salary.calculated_gross = salary.gross_amount + salary.taxes  # npr. polje samo za prikaz
        salary.save()
    return render(request, "financije/view_salaries.html", {"salaries": salaries})


"""Views for the financije app.

This module mixes classic Django views and DRF viewsets. Duplicate viewset
definitions and undefined symbols have been cleaned up.
"""


# REST FRAMEWORK VIEWSETS (single definitions only)


class TenantQuerysetMixin:
    def get_queryset(self):
        qs = super().get_queryset()
        tenant = getattr(self.request, "tenant", None)
        return qs.filter(tenant=tenant) if tenant else qs.none()


class InvoiceViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class AuditLogViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = AuditLog.objects.all()
    serializer_class = AuditLogSerializer


class SalaryViewSet(viewsets.ModelViewSet):
    queryset = Salary.objects.all()
    serializer_class = SalarySerializer


class TaxViewSet(viewsets.ModelViewSet):
    queryset = Tax.objects.all()
    serializer_class = TaxSerializer


class SalaryAdditionViewSet(viewsets.ModelViewSet):
    queryset = SalaryAddition.objects.all()
    serializer_class = SalaryAdditionSerializer


class TaxConfigurationViewSet(viewsets.ModelViewSet):
    queryset = TaxConfiguration.objects.all()
    serializer_class = TaxConfigurationSerializer


class VariablePayRuleViewSet(viewsets.ModelViewSet):
    queryset = VariablePayRule.objects.all()
    serializer_class = VariablePayRuleSerializer


class FinancialReportViewSet(viewsets.ModelViewSet):
    queryset = FinancialReport.objects.all()
    serializer_class = FinancialReportSerializer


class DebtViewSet(viewsets.ModelViewSet):
    queryset = Debt.objects.all()
    serializer_class = DebtSerializer


class BankTransactionViewSet(TenantQuerysetMixin, viewsets.ModelViewSet):
    queryset = BankTransaction.objects.all()
    serializer_class = BankTransactionSerializer


class OverheadCategoryViewSet(viewsets.ModelViewSet):
    queryset = OverheadCategory.objects.all()
    serializer_class = OverheadCategorySerializer


class MonthlyOverheadViewSet(viewsets.ModelViewSet):
    queryset = MonthlyOverhead.objects.all()
    serializer_class = MonthlyOverheadSerializer


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer


@api_view(["GET"])
def trial_balance_view(request):
    tenant = getattr(request, "tenant", None)
    start = request.query_params.get("start")
    end = request.query_params.get("end")
    start_date = None
    end_date = None
    if start:
        from datetime import date

        y, m, d = map(int, start.split("-"))
        start_date = date(y, m, d)
    if end:
        from datetime import date

        y, m, d = map(int, end.split("-"))
        end_date = date(y, m, d)
    data = trial_balance(tenant=tenant, start_date=start_date, end_date=end_date)
    # Serialize dataclasses to dicts
    lines = [
        {
            "account": f"{ln.account_number} {ln.account_name}",
            "number": ln.account_number,
            "name": ln.account_name,
            "type": ln.account_type,
            "debit": str(ln.debit),
            "credit": str(ln.credit),
            "balance": str(ln.balance),
        }
        for ln in data["lines"]
    ]
    return Response(
        {
            "total_debit": str(data["total_debit"]),
            "total_credit": str(data["total_credit"]),
            "lines": lines,
        }
    )


@api_view(["GET"])
def trial_balance_csv_view(request):
    import csv
    from io import StringIO

    tenant = getattr(request, "tenant", None)
    start = request.query_params.get("start")
    end = request.query_params.get("end")
    start_date = None
    end_date = None
    if start:
        from datetime import date

        y, m, d = map(int, start.split("-"))
        start_date = date(y, m, d)
    if end:
        from datetime import date

        y, m, d = map(int, end.split("-"))
        end_date = date(y, m, d)
    data = trial_balance(tenant=tenant, start_date=start_date, end_date=end_date)
    sio = StringIO()
    writer = csv.writer(sio)
    writer.writerow(["Number", "Name", "Type", "Debit", "Credit", "Balance"])
    for ln in data["lines"]:
        writer.writerow(
            [
                ln.account_number,
                ln.account_name,
                ln.account_type,
                str(ln.debit),
                str(ln.credit),
                str(ln.balance),
            ]
        )
    resp = Response(sio.getvalue())
    resp["Content-Type"] = "text/csv"
    resp["Content-Disposition"] = "attachment; filename=trial_balance.csv"
    return resp


@api_view(["GET"])
def general_ledger_view(request, account_number: str):
    tenant = getattr(request, "tenant", None)
    start = request.query_params.get("start")
    end = request.query_params.get("end")
    start_date = None
    end_date = None
    if start:
        from datetime import date

        y, m, d = map(int, start.split("-"))
        start_date = date(y, m, d)
    if end:
        from datetime import date

        y, m, d = map(int, end.split("-"))
        end_date = date(y, m, d)
    data = general_ledger(
        tenant=tenant, account_number=account_number, start_date=start_date, end_date=end_date
    )
    lines = [
        {
            "date": str(ln.date),
            "description": ln.description,
            "debit": str(ln.debit),
            "credit": str(ln.credit),
            "balance": str(ln.balance),
        }
        for ln in data["lines"]
    ]
    return Response(
        {
            "account": data.get("account"),
            "name": data.get("name"),
            "type": data.get("type"),
            "opening_balance": str(data.get("opening_balance", "0.00")),
            "closing_balance": str(data.get("closing_balance", "0.00")),
            "lines": lines,
        }
    )


@api_view(["GET"])
def general_ledger_csv_view(request, account_number: str):
    import csv
    from io import StringIO

    tenant = getattr(request, "tenant", None)
    start = request.query_params.get("start")
    end = request.query_params.get("end")
    start_date = None
    end_date = None
    if start:
        from datetime import date

        y, m, d = map(int, start.split("-"))
        start_date = date(y, m, d)
    if end:
        from datetime import date

        y, m, d = map(int, end.split("-"))
        end_date = date(y, m, d)
    data = general_ledger(
        tenant=tenant, account_number=account_number, start_date=start_date, end_date=end_date
    )
    sio = StringIO()
    writer = csv.writer(sio)
    writer.writerow(["Date", "Description", "Debit", "Credit", "Balance"])
    for ln in data["lines"]:
        writer.writerow(
            [str(ln.date), ln.description, str(ln.debit), str(ln.credit), str(ln.balance)]
        )
    resp = Response(sio.getvalue())
    resp["Content-Type"] = "text/csv"
    resp["Content-Disposition"] = f"attachment; filename=ledger_{account_number}.csv"
    return resp


# Primjer klasičnog CBV za kreiranje Invoice-a
class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = "financije/invoice_form.html"
    success_url = reverse_lazy("financije:invoice_list")


# Primjer lazy importa unutar metode (da izbjegnemo circular import)
def tax_configuration_view(request):
    # koristite 'Employee' po potrebi
    return render(request, "financije/tax_configuration.html", {})


def invoice_list(request):
    invoices = Invoice.objects.all()
    return render(request, "financije/invoice_list.html", {"invoices": invoices})


def invoice_create(request):
    if request.method == "POST":
        form = InvoiceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("invoice_list")
    else:
        form = InvoiceForm()
    return render(request, "financije/invoice_form.html", {"form": form})


def overhead_list(request):
    overheads = Overhead.objects.all()
    return render(request, "financije/overhead_list.html", {"overheads": overheads})


def overhead_create(request):
    if request.method == "POST":
        form = OverheadForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("overhead_list")
    else:
        form = OverheadForm()
    return render(request, "financije/overhead_form.html", {"form": form})


@login_required
def dashboard(request):
    context = {
        "total_invoices": Invoice.objects.count(),
        "unpaid_invoices": Invoice.objects.filter(paid=False).count(),
        "recent_transactions": BankTransaction.objects.all()[:5],
    }
    return render(request, "financije/dashboard.html", context)


# Budgets
class BudgetListView(View):
    def get(self, request):
        budgets = Budget.objects.all()
        return render(request, "financije/budgets.html", {"budgets": budgets})


class BudgetCreateView(View):
    def get(self, request):
        form = BudgetForm()
        return render(request, "financije/budget_form.html", {"form": form})

    def post(self, request):
        form = BudgetForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("budgets")
        return render(request, "financije/budget_form.html", {"form": form})


class BudgetUpdateView(View):
    def get(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk)
        form = BudgetForm(instance=budget)
        return render(request, "financije/budget_form.html", {"form": form})

    def post(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk)
        form = BudgetForm(request.POST, instance=budget)
        if form.is_valid():
            form.save()
            return redirect("budgets")
        return render(request, "financije/budget_form.html", {"form": form})


class BudgetDeleteView(View):
    def get(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk)
        return render(request, "financije/budget_confirm_delete.html", {"budget": budget})

    def post(self, request, pk):
        budget = get_object_or_404(Budget, pk=pk)
        budget.delete()
        return redirect("budgets")


class DebtManagementView(View):
    def get(self, request):
        debts = Debt.objects.all()
        return render(request, "financije/debt_management.html", {"debts": debts})

    # POST for create/update could be added here


# ViewSet za FinancialReport, ako koristite DRF:


"""Duplicate viewset definitions removed above."""


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "financije/invoice_list.html"
    context_object_name = "invoices"
    ordering = ["-issue_date"]


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = "financije/invoice_detail.html"
    context_object_name = "invoice"


class FinancialReportListView(LoginRequiredMixin, ListView):
    model = FinancialReport
    template_name = "financije/financial_report_list.html"
    context_object_name = "reports"
    ordering = ["-year", "-month"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Financial Reports"
        return context


class FinancialReportDetailView(LoginRequiredMixin, DetailView):
    model = FinancialReport
    template_name = "financije/financial_report_detail.html"
    context_object_name = "report"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        report = self.get_object()

        # Add any additional context you need
        context["title"] = f"Financial Report - {report.year}"
        context["cash_flow_data"] = {
            "income": report.priljev_ukupno,
            "expenses": report.odljev_ukupno,
            "net": report.neto_cash_flow,
        }

        return context


class FinancialReportCreateView(LoginRequiredMixin, CreateView):
    model = FinancialReport
    template_name = "financije/financial_report_form.html"
    fields = ["period", "year", "month", "kvartal"]
    success_url = reverse_lazy("financije:financial_report_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.generiraj_izvještaj()  # Pozivamo metodu za generiranje nakon spremanja
        return response


class FinancialReportUpdateView(LoginRequiredMixin, UpdateView):
    model = FinancialReport
    template_name = "financije/financial_report_form.html"
    fields = ["period", "year", "month", "kvartal"]
    success_url = reverse_lazy("financije:financial_report_list")

    def form_valid(self, form):
        response = super().form_valid(form)
        self.object.generiraj_izvještaj()  # Regeneriramo izvještaj nakon ažuriranja
        return response


class BankTransactionListView(LoginRequiredMixin, ListView):
    model = BankTransaction
    template_name = "financije/bank_transaction_list.html"
    context_object_name = "transactions"
    ordering = ["-datum_transakcije"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = "Bank Transactions"
        return context


class CashFlowView(LoginRequiredMixin, View):
    def get(self, request):
        cash_flows = CashFlow.objects.all().order_by("-datum")
        context = {"cash_flows": cash_flows, "title": "Cash Flow"}
        return render(request, "financije/cash_flow.html", context)


class TaxConfigurationListView(LoginRequiredMixin, ListView):
    model = TaxConfiguration
    template_name = "financije/tax_configuration_list.html"
    context_object_name = "tax_configurations"
    ordering = ["name"]
