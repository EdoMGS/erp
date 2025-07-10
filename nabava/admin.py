# nabava/admin.py

from django.contrib import admin

from .forms import (ProcurementPlanForm, ProcurementRequestForm,
                    PurchaseOrderForm)
from .models import (Dobavljac, GrupaDobavljaca, Narudzbenica,
                     NarudzbenicaStavka, ProcurementPlan, ProcurementRequest,
                     PurchaseOrder, PurchaseOrderLine)


@admin.register(ProcurementPlan)
class ProcurementPlanAdmin(admin.ModelAdmin):
    form = ProcurementPlanForm
    list_display = [
        "project_name",
        "item",
        "quantity",
        "required_date",
        "status",
        "priority",
    ]
    search_fields = ["project_name", "item"]
    list_filter = ["status", "required_date", "priority"]


@admin.register(ProcurementRequest)
class ProcurementRequestAdmin(admin.ModelAdmin):
    form = ProcurementRequestForm
    list_display = [
        "procurement_plan",
        "item",
        "quantity",
        "department",
        "status",
        "request_date",
    ]
    list_filter = ["status", "request_date"]
    search_fields = ["item", "department"]


@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    form = PurchaseOrderForm
    list_display = ["id", "supplier", "order_date", "status", "is_jit"]
    list_filter = ["status", "is_jit", "order_date"]
    search_fields = ["supplier__naziv"]


@admin.register(Narudzbenica)
class NarudzbenicaAdmin(admin.ModelAdmin):
    list_display = ["broj", "datum", "dobavljac", "status"]
    list_filter = ["status", "datum"]
    search_fields = ["broj", "dobavljac__naziv"]


@admin.register(NarudzbenicaStavka)
class NarudzbenicaStavkaAdmin(admin.ModelAdmin):
    list_display = ["narudzbenica", "artikl", "kolicina", "cijena"]
    search_fields = ["narudzbenica__broj", "artikl__naziv"]


@admin.register(Dobavljac)
class DobavljacAdmin(admin.ModelAdmin):
    list_display = ["naziv", "oib", "grad", "rejting", "is_active"]
    list_filter = ["rejting", "is_active", "grupa"]
    search_fields = ["naziv", "oib"]


@admin.register(GrupaDobavljaca)
class GrupaDobavljacaAdmin(admin.ModelAdmin):
    list_display = ["naziv", "is_active"]
    search_fields = ["naziv"]


@admin.register(PurchaseOrderLine)
class PurchaseOrderLineAdmin(admin.ModelAdmin):
    list_display = ["purchase_order", "artikl", "quantity", "unit_price", "discount"]
    list_filter = ["purchase_order__status"]
    search_fields = ["artikl__naziv"]
