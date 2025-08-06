from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import CreateView, TemplateView
from rest_framework import generics, viewsets

from .forms import DobavljacForm, GrupaDobavljacaForm, NarudzbenicaForm, NarudzbenicaStavkaForm, PurchaseOrderForm
from .models import (
    Dobavljac,
    GrupaDobavljaca,
    Narudzbenica,
    NarudzbenicaStavka,
    ProcurementPlan,
    ProcurementRequest,
    PurchaseOrder,
    PurchaseOrderLine,
)
from .serializers import (
    DobavljacSerializer,
    GrupaDobavljacaSerializer,
    NarudzbenicaSerializer,
    NarudzbenicaStavkaSerializer,
    ProcurementPlanSerializer,
    ProcurementRequestSerializer,
    PurchaseOrderLineSerializer,
    PurchaseOrderSerializer,
)


class ProcurementPlanViewSet(viewsets.ModelViewSet):
    queryset = ProcurementPlan.objects.all()
    serializer_class = ProcurementPlanSerializer


class ProcurementRequestViewSet(viewsets.ModelViewSet):
    queryset = ProcurementRequest.objects.all()
    serializer_class = ProcurementRequestSerializer


# Removed SupplierViewSet class
class PurchaseOrderViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer


class NarudzbenicaViewSet(viewsets.ModelViewSet):
    queryset = Narudzbenica.objects.all()
    serializer_class = NarudzbenicaSerializer


class NarudzbenicaStavkaViewSet(viewsets.ModelViewSet):
    queryset = NarudzbenicaStavka.objects.all()
    serializer_class = NarudzbenicaStavkaSerializer


class PurchaseOrderLineViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrderLine.objects.all()
    serializer_class = PurchaseOrderLineSerializer


class DobavljacViewSet(viewsets.ModelViewSet):
    queryset = Dobavljac.objects.all()
    serializer_class = DobavljacSerializer


class GrupaDobavljacaViewSet(viewsets.ModelViewSet):
    queryset = GrupaDobavljaca.objects.all()
    serializer_class = GrupaDobavljacaSerializer


class NabavaHomeView(TemplateView):
    template_name = "nabava_home.html"


class OrderCreateView(CreateView):
    model = PurchaseOrder
    form_class = PurchaseOrderForm
    template_name = "nabava/purchaseorder_form.html"
    success_url = "/purchaseorder/list/"


def nabava_home(request):
    return render(request, "nabava_home.html")


@login_required
def procurement_dashboard(request):
    context = {
        "recent_orders": PurchaseOrder.objects.all()[:5],
        "recent_plans": ProcurementPlan.objects.all()[:5],
        "pending_orders": PurchaseOrder.objects.filter(status="in_preparation").count(),
    }
    return render(request, "nabava/dashboard.html", context)


@login_required
def purchaseorder_list(request):
    purchaseorders = PurchaseOrder.objects.all()
    return render(request, "nabava/purchaseorder_list.html", {"purchaseorders": purchaseorders})


@login_required
def purchaseorder_create(request):
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("purchaseorder_list")
    else:
        form = PurchaseOrderForm()
    return render(request, "nabava/purchaseorder_form.html", {"form": form})


@login_required
def purchase_order_list(request):
    orders = PurchaseOrder.objects.all().order_by("-order_date")
    return render(request, "nabava/purchase_order_list.html", {"orders": orders})


@login_required
def purchase_order_create(request):
    if request.method == "POST":
        form = PurchaseOrderForm(request.POST)
        if form.is_valid():
            order = form.save()
            messages.success(request, "Narudžba uspješno kreirana.")
            return redirect("nabava:order_detail", pk=order.pk)
    else:
        form = PurchaseOrderForm()
    return render(request, "nabava/purchase_order_form.html", {"form": form})


@login_required
def narudzbenica_create(request):
    if request.method == "POST":
        form = NarudzbenicaForm(request.POST)
        if form.is_valid():
            narudzbenica = form.save()
            messages.success(request, "Narudžbenica je uspješno kreirana.")
            return redirect("nabava:narudzbenica_detail", pk=narudzbenica.pk)
    else:
        form = NarudzbenicaForm()
    return render(request, "nabava/narudzbenica_form.html", {"form": form})


@login_required
def add_stavka(request, pk):
    narudzbenica = get_object_or_404(Narudzbenica, pk=pk)
    if request.method == "POST":
        form = NarudzbenicaStavkaForm(request.POST)
        if form.is_valid():
            stavka = form.save(commit=False)
            stavka.narudzbenica = narudzbenica
            stavka.save()
            messages.success(request, "Stavka je dodana.")
            return redirect("nabava:narudzbenica_detail", pk=pk)
    else:
        form = NarudzbenicaStavkaForm()
    return render(request, "nabava/stavka_form.html", {"form": form, "narudzbenica": narudzbenica})


@login_required
def dobavljac_list(request):
    dobavljaci = Dobavljac.objects.filter(is_active=True)
    return render(request, "nabava/dobavljac_list.html", {"dobavljaci": dobavljaci})


@login_required
def dobavljac_create(request):
    if request.method == "POST":
        form = DobavljacForm(request.POST)
        if form.is_valid():
            dobavljac = form.save()
            messages.success(request, "Dobavljač uspješno kreiran.")
            return redirect("nabava:dobavljac_detail", pk=dobavljac.pk)
    else:
        form = DobavljacForm()
    return render(request, "nabava/dobavljac_form.html", {"form": form})


@login_required
def dobavljac_edit(request, pk):
    dobavljac = get_object_or_404(Dobavljac, pk=pk)
    if request.method == "POST":
        form = DobavljacForm(request.POST, instance=dobavljac)
        if form.is_valid():
            form.save()
            messages.success(request, "Dobavljač uspješno ažuriran.")
            return redirect("nabava:dobavljac_detail", pk=pk)
    else:
        form = DobavljacForm(instance=dobavljac)
    return render(
        request,
        "nabava/dobavljac_form.html",
        {"form": form, "dobavljac": dobavljac, "edit_mode": True},
    )


@login_required
def grupa_dobavljaca_list(request):
    grupe = GrupaDobavljaca.objects.filter(is_active=True)
    return render(request, "nabava/grupa_dobavljaca_list.html", {"grupe": grupe})


@login_required
def procurement_plan_list(request):
    plans = ProcurementPlan.objects.all().order_by("-required_date")
    return render(request, "nabava/procurement_plan_list.html", {"plans": plans})


@login_required
def procurement_plan_create(request):
    if request.method == "POST":
        form = ProcurementPlanForm(request.POST)
        if form.is_valid():  # Ispravljeno is_valid() umjesto is_valid()
            plan = form.save()
            messages.success(request, "Plan nabave uspješno kreiran.")
            return redirect("nabava:plan_detail", pk=plan.pk)
    else:
        form = ProcurementPlanForm()
    return render(request, "nabava/procurement_plan_form.html", {"form": form})


@login_required
def procurement_plan_detail(request, pk):
    plan = get_object_or_404(ProcurementPlan, pk=pk)
    return render(request, "nabava/procurement_plan_detail.html", {"plan": plan})


@login_required
def purchase_order_detail(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    return render(request, "nabava/purchase_order_detail.html", {"order": order})


@login_required
def narudzbenica_list(request):
    narudzbenice = Narudzbenica.objects.all().order_by("-datum")
    return render(request, "nabava/narudzbenica_list.html", {"narudzbenice": narudzbenice})


@login_required
def narudzbenica_detail(request, pk):
    narudzbenica = get_object_or_404(Narudzbenica, pk=pk)
    return render(request, "nabava/narudzbenica_detail.html", {"narudzbenica": narudzbenica})


@login_required
def dobavljac_detail(request, pk):
    dobavljac = get_object_or_404(Dobavljac, pk=pk)
    return render(request, "nabava/dobavljac_detail.html", {"dobavljac": dobavljac})


@login_required
def grupa_dobavljaca_create(request):
    if request.method == "POST":
        form = GrupaDobavljacaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Grupa dobavljača uspješno kreirana.")
            return redirect("nabava:grupa_list")
    else:
        form = GrupaDobavljacaForm()
    return render(request, "nabava/grupa_dobavljaca_form.html", {"form": form})


@login_required
def purchase_order_add_line(request, pk):
    order = get_object_or_404(PurchaseOrder, pk=pk)
    if request.method == "POST":
        form = PurchaseOrderLineForm(request.POST)
        if form.is_valid():
            line = form.save(commit=False)
            line.purchase_order = order
            line.save()
            messages.success(request, "Stavka je dodana u narudžbu.")
            return redirect("nabava:order_detail", pk=pk)
    else:
        form = PurchaseOrderLineForm()
    return render(request, "nabava/purchase_order_line_form.html", {"form": form, "order": order})


@login_required
def grupa_dobavljaca_detail(request, pk):
    grupa = get_object_or_404(GrupaDobavljaca, pk=pk)
    dobavljaci = grupa.dobavljaci.filter(is_active=True)  # Dohvaća povezane dobavljače
    return render(
        request,
        "nabava/grupa_dobavljaca_detail.html",
        {"grupa": grupa, "dobavljaci": dobavljaci},
    )


# API Views
class PurchaseOrderListAPI(generics.ListCreateAPIView):
    queryset = PurchaseOrder.objects.all()
    serializer_class = PurchaseOrderSerializer


class ProcurementPlanListAPI(generics.ListCreateAPIView):
    queryset = ProcurementPlan.objects.all()
    serializer_class = ProcurementPlanSerializer
