# prodaja/urls.py
from django.urls import path

from . import views

app_name = "prodaja"

urlpatterns = [
    path("", views.prodaja_home, name="prodaja-home"),
    # SalesOpportunity
    path("opportunity/", views.opportunity_list, name="opportunity_list"),
    path("opportunity/create/", views.opportunity_create, name="opportunity_create"),
    path("opportunity/<int:pk>/edit/", views.opportunity_edit, name="opportunity_edit"),
    path("opportunity/<int:pk>/", views.opportunity_detail, name="opportunity_detail"),
    path(
        "opportunity/<int:pk>/delete/",
        views.opportunity_delete,
        name="opportunity_delete",
    ),
    # FieldVisit
    path(
        "opportunity/<int:opportunity_id>/fieldvisit/new/",
        views.fieldvisit_create,
        name="fieldvisit_create",
    ),
    # Quotation
    path("quotation/", views.quotation_list, name="quotation_list"),
    path("quotation/create/", views.quotation_create, name="quotation_create"),
    path("quotation/<int:pk>/edit/", views.quotation_edit, name="quotation_edit"),
    path("quotation/<int:pk>/", views.quotation_detail, name="quotation_detail"),
    path("quotation/<int:pk>/delete/", views.quotation_delete, name="quotation_delete"),
    # SalesOrder
    path("salesorder/", views.salesorder_list, name="salesorder_list"),
    path("salesorder/create/", views.salesorder_create, name="salesorder_create"),
    path("salesorder/<int:pk>/edit/", views.salesorder_edit, name="salesorder_edit"),
    path("salesorder/<int:pk>/", views.salesorder_detail, name="salesorder_detail"),
    path("salesorder/<int:pk>/delete/", views.salesorder_delete, name="salesorder_delete"),
    # SalesContract
    path("salescontract/", views.salescontract_list, name="salescontract_list"),
    path("salescontract/create/", views.salescontract_create, name="salescontract_create"),
    path(
        "salescontract/<int:pk>/edit/",
        views.salescontract_edit,
        name="salescontract_edit",
    ),
    path(
        "salescontract/<int:pk>/",
        views.salescontract_detail,
        name="salescontract_detail",
    ),
    path(
        "salescontract/<int:pk>/delete/",
        views.salescontract_delete,
        name="salescontract_delete",
    ),
    # Tender patterns
    path("tender/", views.tender_preparation_unified, name="tender_create"),
    path(
        "tender/<int:pk>/<str:action>/",
        views.tender_preparation_unified,
        name="tender_preparation",
    ),
    path("tender/list/", views.tender_preparation_list, name="tender_list"),
    path("tender/<int:pk>/calculator/", views.tender_calculator, name="tender_calculate"),
    path("tender/<int:pk>/update/", views.update_tender_data, name="update_tender_data"),
    path("api/supplier-prices/", views.fetch_supplier_prices, name="supplier_prices"),
]
