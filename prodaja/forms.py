from django import forms
from django.forms import ModelForm

from .models import (
    FieldVisit,
    Offer,
    Quotation,
    SalesContract,
    SalesOpportunity,
    SalesOrder,
)

# MVP-only forms


class OpportunityForm(ModelForm):
    class Meta:
        model = SalesOpportunity
        fields = [
            "name",
            "client_name",
            "lead_source",
            "stage",
            "amount",
            "budget_estimate",
            "public_tender_number",
            "project_service_type",
            "notes",
        ]


class FieldVisitForm(ModelForm):
    class Meta:
        model = FieldVisit
        fields = ["opportunity", "scheduled_date", "status", "notes"]
        widgets = {"scheduled_date": forms.DateInput(attrs={"type": "date"})}


class QuotationForm(ModelForm):
    class Meta:
        model = Quotation
        fields = [
            "client_name",
            "opportunity",
            "quote_number",
            "valid_until",
            "status",
            "total_amount",
            "discount",
            "revision_count",
            "created_by",
            "linked_production_order_ref",
        ]
        widgets = {"valid_until": forms.DateInput(attrs={"type": "date"})}


class SalesOrderForm(ModelForm):
    class Meta:
        model = SalesOrder
        fields = [
            "client_name",
            "order_number",
            "status",
            "total_amount",
            "discount",
            "created_by",
            "quotation",
            "date_approved_by_client",
        ]
        widgets = {"date_approved_by_client": forms.DateInput(attrs={"type": "date"})}


class SalesContractForm(ModelForm):
    class Meta:
        model = SalesContract
        fields = [
            "client_name",
            "contract_number",
            "status",
            "public_tender_number",
            "bank_guarantee_required",
            "total_amount",
            "discount",
            "sales_order",
            "delivery_schedule",
            "client_specific_reqs",
            "related_production_order_ref",
            "created_by",
        ]


class OfferForm(ModelForm):
    class Meta:
        model = Offer
        fields = [
            "customer_name",
            "service_lines",
            "material_lines",
            "total_amount",
            "status",
        ]

    # All legacy tender/work order related forms & formsets removed for MVP.

    # No extra clean logic needed for MVP
