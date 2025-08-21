import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt

from .forms import (
    FieldVisitForm,
    OpportunityForm,
    QuotationForm,
    SalesContractForm,
    SalesOrderForm,
    TenderCostFormSet,
    TenderDocumentFormSet,
    TenderLaborFormSet,
    TenderMaterialFormSet,
    TenderNeposredniFormSet,
    TenderPosredniFormSet,
    TenderPreparationForm,
    TenderRasclambaFormSet,
)
from .models import Quotation, SalesContract, SalesOpportunity, SalesOrder, TenderPreparation

########################################
# OPPORTUNITY VIEWS
########################################


@login_required
def opportunity_list(request):
    opportunities = SalesOpportunity.objects.all()
    return render(request, "prodaja/opportunity_list.html", {"opportunities": opportunities})


@login_required
def opportunity_create(request):
    if request.method == "POST":
        form = OpportunityForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Lead je uspješno kreiran!")
            return redirect("prodaja:opportunity_list")
    else:
        form = OpportunityForm()
    return render(request, "prodaja/opportunity_form.html", {"form": form, "action": "create"})


@login_required
def opportunity_edit(request, pk):
    obj = get_object_or_404(SalesOpportunity, pk=pk)
    if request.method == "POST":
        form = OpportunityForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Lead je uspješno ažuriran!")
            return redirect("prodaja:opportunity_list")
    else:
        form = OpportunityForm(instance=obj)
    return render(
        request,
        "prodaja/opportunity_form.html",
        {"form": form, "action": "edit", "opportunity": obj},
    )


@login_required
def opportunity_detail(request, pk):
    obj = get_object_or_404(SalesOpportunity, pk=pk)
    visits = obj.field_visits.all()
    return render(
        request,
        "prodaja/opportunity_detail.html",
        {"opportunity": obj, "visits": visits},
    )


@login_required
def opportunity_delete(request, pk):
    obj = get_object_or_404(SalesOpportunity, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.warning(request, "Lead je obrisan!")
        return redirect("prodaja:opportunity_list")
    return render(
        request,
        "prodaja/confirm_delete.html",
        {"object": obj, "object_type": "Opportunity"},
    )


########################################
# FIELD VISIT VIEWS
########################################


@login_required
def fieldvisit_create(request, opportunity_id=None):
    opportunity_obj = None
    if opportunity_id:
        opportunity_obj = get_object_or_404(SalesOpportunity, pk=opportunity_id)
    if request.method == "POST":
        form = FieldVisitForm(request.POST)
        if form.is_valid():
            visit = form.save()
            messages.success(request, "Terenska posjeta je uspješno evidentirana.")
            return redirect(
                "prodaja:opportunity_detail",
                pk=visit.opportunity.id if visit.opportunity else opportunity_id,
            )
    else:
        initial_data = {}
        if opportunity_obj:
            initial_data["opportunity"] = opportunity_obj
        form = FieldVisitForm(initial=initial_data)
    return render(
        request,
        "prodaja/fieldvisit_form.html",
        {"form": form, "opportunity": opportunity_obj},
    )


########################################
# QUOTATION VIEWS
########################################


@login_required
def quotation_list(request):
    qs = Quotation.objects.all().order_by("-created_at")
    return render(request, "prodaja/quotation_list.html", {"quotations": qs})


@login_required
def quotation_create(request):
    if request.method == "POST":
        form = QuotationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ponuda je kreirana.")
            return redirect("prodaja:quotation_list")
    else:
        form = QuotationForm()
    return render(request, "prodaja/quotation_form.html", {"form": form, "action": "create"})


@login_required
def quotation_edit(request, pk):
    obj = get_object_or_404(Quotation, pk=pk)
    if request.method == "POST":
        form = QuotationForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Ponuda je ažurirana.")
            return redirect("prodaja:quotation_list")
    else:
        form = QuotationForm(instance=obj)
    return render(
        request,
        "prodaja/quotation_form.html",
        {"form": form, "action": "edit", "quotation": obj},
    )


@login_required
def quotation_detail(request, pk):
    obj = get_object_or_404(Quotation, pk=pk)
    return render(request, "prodaja/quotation_detail.html", {"quotation": obj})


@login_required
def quotation_delete(request, pk):
    obj = get_object_or_404(Quotation, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.warning(request, "Ponuda je obrisana!")
        return redirect("prodaja:quotation_list")
    return render(
        request,
        "prodaja/confirm_delete.html",
        {"object": obj, "object_type": "Quotation"},
    )


########################################
# SALES ORDER VIEWS
########################################


@login_required
def salesorder_list(request):
    qs = SalesOrder.objects.all().order_by("-created_at")
    return render(request, "prodaja/salesorder_list.html", {"sales_orders": qs})


@login_required
def salesorder_create(request):
    if request.method == "POST":
        form = SalesOrderForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Narudžba je kreirana.")
            return redirect("prodaja:salesorder_list")
    else:
        form = SalesOrderForm()
    return render(request, "prodaja/salesorder_form.html", {"form": form, "action": "create"})


@login_required
def salesorder_edit(request, pk):
    obj = get_object_or_404(SalesOrder, pk=pk)
    if request.method == "POST":
        form = SalesOrderForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Narudžba je ažurirana.")
            return redirect("prodaja:salesorder_list")
    else:
        form = SalesOrderForm(instance=obj)
    return render(
        request,
        "prodaja/salesorder_form.html",
        {"form": form, "action": "edit", "sales_order": obj},
    )


@login_required
def salesorder_detail(request, pk):
    obj = get_object_or_404(SalesOrder, pk=pk)
    return render(request, "prodaja/salesorder_detail.html", {"sales_order": obj})


@login_required
def salesorder_delete(request, pk):
    obj = get_object_or_404(SalesOrder, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.warning(request, "Narudžba je obrisana!")
        return redirect("prodaja:salesorder_list")
    return render(
        request,
        "prodaja/confirm_delete.html",
        {"object": obj, "object_type": "SalesOrder"},
    )


########################################
# SALES CONTRACT VIEWS
########################################


@login_required
def salescontract_list(request):
    qs = SalesContract.objects.all().order_by("-created_at")
    return render(request, "prodaja/salescontract_list.html", {"sales_contracts": qs})


@login_required
def salescontract_create(request):
    if request.method == "POST":
        form = SalesContractForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Ugovor je kreiran.")
            return redirect("prodaja:salescontract_list")
    else:
        form = SalesContractForm()
    return render(request, "prodaja/salescontract_form.html", {"form": form, "action": "create"})


@login_required
def salescontract_edit(request, pk):
    obj = get_object_or_404(SalesContract, pk=pk)
    if request.method == "POST":
        form = SalesContractForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Ugovor je ažuriran.")
            return redirect("prodaja:salescontract_list")
    else:
        form = SalesContractForm(instance=obj)
    return render(
        request,
        "prodaja/salescontract_form.html",
        {"form": form, "action": "edit", "sales_contract": obj},
    )


@login_required
def salescontract_detail(request, pk):
    obj = get_object_or_404(SalesContract, pk=pk)
    return render(request, "prodaja/salescontract_detail.html", {"sales_contract": obj})


@login_required
def salescontract_delete(request, pk):
    obj = get_object_or_404(SalesContract, pk=pk)
    if request.method == "POST":
        obj.delete()
        messages.warning(request, "Ugovor je obrisan!")
        return redirect("prodaja:salescontract_list")
    return render(
        request,
        "prodaja/confirm_delete.html",
        {"object": obj, "object_type": "SalesContract"},
    )


########################################
# TENDER PREPARATION VIEWS
########################################


@login_required
def tender_preparation_unified(request, pk=None, action="create"):
    tender = get_object_or_404(TenderPreparation, pk=pk) if pk else None

    if request.method == "POST" and action != "view":
        if "change_status" in request.POST:
            try:
                new_status = request.POST.get("new_status")
                tender.change_status(new_status, request.user)
                messages.success(request, f"Status changed to {new_status}")
                return redirect("prodaja:tender_preparation", pk=tender.pk, action="view")
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect("prodaja:tender_preparation", pk=tender.pk, action="view")

        form = TenderPreparationForm(request.POST, request.FILES, instance=tender)
        document_formset = TenderDocumentFormSet(request.POST, request.FILES, instance=tender)
        material_formset = TenderMaterialFormSet(request.POST, prefix="material", instance=tender)
        labor_formset = TenderLaborFormSet(request.POST, prefix="labor", instance=tender)
        cost_formset = TenderCostFormSet(request.POST, prefix="cost", instance=tender)
        rasclamba_formset = TenderRasclambaFormSet(
            request.POST, prefix="rasclamba", instance=tender
        )
        neposredni_formset = TenderNeposredniFormSet(
            request.POST, prefix="neposredni", instance=tender
        )
        posredni_formset = TenderPosredniFormSet(request.POST, prefix="posredni", instance=tender)

        if all(
            [
                form.is_valid(),
                document_formset.is_valid(),
                material_formset.is_valid(),
                labor_formset.is_valid(),
                cost_formset.is_valid(),
                rasclamba_formset.is_valid(),
                neposredni_formset.is_valid(),
                posredni_formset.is_valid(),
            ]
        ):
            with transaction.atomic():
                tender = form.save()
                document_formset.save()
                material_formset.save()
                labor_formset.save()
                cost_formset.save()
                rasclamba_formset.save()
                neposredni_formset.save()
                posredni_formset.save()
                if hasattr(tender, "tender_summary"):
                    tender.tender_summary.update_costs()
            messages.success(request, "Tender je uspješno spremljen.")
            return redirect("prodaja:tender_preparation", pk=tender.pk, action="view")
    else:
        form = TenderPreparationForm(instance=tender)
        document_formset = TenderDocumentFormSet(instance=tender)
        material_formset = TenderMaterialFormSet(prefix="material", instance=tender)
        labor_formset = TenderLaborFormSet(prefix="labor", instance=tender)
        cost_formset = TenderCostFormSet(prefix="cost", instance=tender)
        rasclamba_formset = TenderRasclambaFormSet(prefix="rasclamba", instance=tender)
        neposredni_formset = TenderNeposredniFormSet(prefix="neposredni", instance=tender)
        posredni_formset = TenderPosredniFormSet(prefix="posredni", instance=tender)

    context = {
        "form": form,
        "document_formset": document_formset,
        "material_formset": material_formset,
        "labor_formset": labor_formset,
        "cost_formset": cost_formset,
        "rasclamba_formset": rasclamba_formset,
        "neposredni_formset": neposredni_formset,
        "posredni_formset": posredni_formset,
        "action": action,
        "tender": tender,
        "status_history": tender.tenderstatuschange_set.all() if tender else None,
    }
    return render(request, "prodaja/tender_preparation_unified.html", context)


@login_required
def tender_preparation_list(request):
    """Prikaz liste tender priprema."""
    tenders = TenderPreparation.objects.all()
    return render(request, "prodaja/tender_list.html", {"tenders": tenders})


@login_required
def tender_calculator(request, pk):
    """View za kalkulator troškova tendera."""
    tender = get_object_or_404(TenderPreparation, pk=pk)
    if request.method == "POST":
        material_costs = Decimal(request.POST.get("material_costs", 0))
        labor_hours = Decimal(request.POST.get("labor_hours", 0))
        hourly_rate = Decimal(request.POST.get("hourly_rate", tender.hourly_rate))
        tender.material_costs = material_costs
        tender.labor_hours = labor_hours
        tender.hourly_rate = hourly_rate
        tender.save()
        return JsonResponse(
            {
                "success": True,
                "total_cost": str(tender.total_cost),
                "margin": str(tender.calculate_margin() or 0),
            }
        )
    return render(request, "prodaja/calculator_partial.html", {"tender": tender})


@login_required
def fetch_supplier_prices(request):
    """API endpoint za dohvaćanje cijena dobavljača."""
    item = request.GET.get("item")
    if not item:
        return JsonResponse({"error": "No item specified"}, status=400)
    prices = []  # Implementirajte logiku dohvaćanja cijena s vanjskih servisa
    return JsonResponse({"prices": prices})


# AJAX endpoint za Handsontable update tender podataka
@csrf_exempt  # Ako koristite CSRF token, uklonite ovu dekoraciju i osigurajte da se token šalje
@login_required
def update_tender_data(request, pk):
    if request.method == "POST":
        tender = get_object_or_404(TenderPreparation, pk=pk)
        try:
            payload = json.loads(request.body)
            material_data = payload.get("Materijal", [])
            # Brišemo postojeće materijalne stavke
            from .models import TenderMaterial

            TenderMaterial.objects.filter(tender=tender).delete()
            for row in material_data:
                TenderMaterial.objects.create(
                    tender=tender,
                    item_name=row.get("item_name", ""),
                    unit_price=Decimal(row.get("unit_price") or "0"),
                    quantity=int(row.get("quantity") or 0),
                    tax=Decimal(row.get("tax") or "0"),
                )
            if hasattr(tender, "summary"):
                tender.summary.update_costs()
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)
    return JsonResponse({"success": False}, status=400)


def prodaja_home(request):
    return render(request, "prodaja/home.html")
