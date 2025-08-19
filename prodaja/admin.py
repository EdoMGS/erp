from django.contrib import admin

from .models import (
    FieldVisit,
    Offer,
    Quotation,
    SalesContract,
    SalesOpportunity,
    SalesOrder,
)


@admin.register(SalesOpportunity)
class SalesOpportunityAdmin(admin.ModelAdmin):
    list_display = ("name", "client_name", "stage", "amount")
    search_fields = ("name", "client_name")


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = ("quote_number", "client_name", "status", "total_amount")
    search_fields = ("quote_number", "client_name")


@admin.register(SalesOrder)
class SalesOrderAdmin(admin.ModelAdmin):
    list_display = ("order_number", "client_name", "status", "total_amount")
    search_fields = ("order_number", "client_name")


@admin.register(SalesContract)
class SalesContractAdmin(admin.ModelAdmin):
    list_display = ("contract_number", "client_name", "status", "total_amount")
    search_fields = ("contract_number", "client_name")


@admin.register(FieldVisit)
class FieldVisitAdmin(admin.ModelAdmin):
    list_display = ("opportunity", "scheduled_date", "status")
    search_fields = ("opportunity__name",)


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("id", "customer_name", "status", "total_amount")
    search_fields = ("customer_name",)
