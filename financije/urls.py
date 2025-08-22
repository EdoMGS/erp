from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "financije"

router = DefaultRouter()
router.register(r"financial-reports", views.FinancialReportViewSet)
router.register(r"debts", views.DebtViewSet)
router.register(r"bank-transactions", views.BankTransactionViewSet)
router.register(r"overhead-categories", views.OverheadCategoryViewSet)
router.register(r"monthly-overhead", views.MonthlyOverheadViewSet)
router.register(r"budgets", views.BudgetViewSet)
router.register(r"invoices", views.InvoiceViewSet)
router.register(r"monthly-overheads", views.MonthlyOverheadViewSet)
router.register(r"audit-logs", views.AuditLogViewSet)
router.register(r"salaries", views.SalaryViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("trial-balance/", views.trial_balance_view, name="trial_balance"),
    path("trial-balance.csv", views.trial_balance_csv_view, name="trial_balance_csv"),
    path("ledger/<str:account_number>/", views.general_ledger_view, name="general_ledger"),
    path(
        "ledger/<str:account_number>.csv",
        views.general_ledger_csv_view,
        name="general_ledger_csv",
    ),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("budgets/", views.BudgetListView.as_view(), name="budgets"),
    path("budgets/create/", views.BudgetCreateView.as_view(), name="create_budget"),
    path("budgets/<int:pk>/edit/", views.BudgetUpdateView.as_view(), name="edit_budget"),
    path(
        "budgets/<int:pk>/delete/",
        views.BudgetDeleteView.as_view(),
        name="delete_budget",
    ),
    path("debt-management/", views.DebtManagementView.as_view(), name="debt_management"),
    path("new_invoice/", views.invoice_form, name="new_invoice"),
    path("update_invoice/<int:pk>/", views.invoice_form, name="update_invoice"),
    path(
        "create_invoice_from_quote/<int:quote_id>/",
        views.create_invoice_from_quote,
        name="create_invoice_from_quote",
    ),
    path("view_invoices/", views.view_invoices, name="view_invoices"),
    path("delete_invoice/<int:pk>/", views.delete_invoice, name="delete_invoice"),
    path("view_salaries/", views.view_salaries, name="view_salaries"),
    # Include production app URLs
    # Add URL patterns for any new views added.
    path("invoices/", views.InvoiceListView.as_view(), name="invoice_list"),
    path("invoice/create/", views.InvoiceCreateView.as_view(), name="invoice_create"),
    path("invoice/<int:pk>/", views.InvoiceDetailView.as_view(), name="invoice_detail"),
    path(
        "financial-reports/",
        views.FinancialReportListView.as_view(),
        name="financial_report_list",
    ),
    path(
        "financial-reports/<int:pk>/",
        views.FinancialReportDetailView.as_view(),
        name="financial_report_detail",
    ),
    path(
        "financial-reports/create/",
        views.FinancialReportCreateView.as_view(),
        name="financial_report_create",
    ),
    path(
        "financial-reports/<int:pk>/edit/",
        views.FinancialReportUpdateView.as_view(),
        name="financial_report_edit",
    ),
    path(
        "bank-transactions/",
        views.BankTransactionListView.as_view(),
        name="bank_transaction_list",
    ),
    path("cash-flow/", views.CashFlowView.as_view(), name="cash_flow"),
    path(
        "tax-configurations/",
        views.TaxConfigurationListView.as_view(),
        name="tax_configuration_list",
    ),
]
