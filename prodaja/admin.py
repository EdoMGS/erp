from django.contrib import admin

from .models import SalesContract  # Add new imports
from .models import (Quotation, SalesOpportunity, SalesOrder, TenderDocument,
                     TenderPreparation, WorkOrderInput)


@admin.register(SalesOpportunity)
class SalesOpportunityAdmin(admin.ModelAdmin):
    list_display = ("name", "client", "stage")
    search_fields = ("name", "client__name")


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    search_fields = (
        "quote_number",
        "client__name",
    )  # Changed 'quotation_number' to 'quote_number'


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    search_fields = ("order_number", "client__name")


@admin.register(SalesContract)
class SalesContractAdmin(admin.ModelAdmin):
    search_fields = ("contract_number", "client__name")


@admin.register(WorkOrderInput)
class WorkOrderInputAdmin(admin.ModelAdmin):
    list_display = ("radni_nalog", "proizvod", "kolicina", "cijena")
    search_fields = ("proizvod",)


@admin.register(TenderDocument)
class TenderDocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "uploaded_at")
    readonly_fields = ("uploaded_at",)


@admin.register(TenderPreparation)
class TenderPreparationAdmin(admin.ModelAdmin):
    list_display = ("opportunity", "status", "created_at")
    readonly_fields = ("created_at", "updated_at")
