import logging

import pandas as pd
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DeleteView, ListView, UpdateView
from rest_framework import generics, viewsets

from financije.models import Invoice  # Only for read operations
from prodaja.models import SalesOpportunity, SalesOrder  # Updated to import SalesOrder from prodaja

from .forms import SalesOpportunityForm  # Only forms we actually define in our app
from .forms import ClientSupplierForm
from .models import ClientActivityLog, ClientSupplier
from .serializers import SalesOpportunitySerializer  # Added SalesOpportunitySerializer
from .serializers import SalesOrderSerializer  # Added SalesOrderSerializer
from .serializers import ClientActivityLogSerializer, ClientSupplierSerializer, InvoiceSerializer

logger = logging.getLogger(__name__)


def log_client_activity(client, activity_text, activity_type="other"):
    """Log client activity with proper activity type."""
    log = ClientActivityLog(
        client=client,
        activity=activity_text,
        activity_type=activity_type,
        timestamp=timezone.now(),
    )
    log.save()
    logger.info(f"Activity logged for client {client.name}: {activity_text}")


class BaseListView(ListView):
    paginate_by = 10
    template_name = "client_app/list_view.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "title": self.title,
                "headers": self.headers,
                "create_url": reverse_lazy(self.create_url_name),
            }
        )
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get("q")
        if query:
            queryset = queryset.filter(self.get_search_filter(query))
        return queryset


class ClientListView(BaseListView):
    model = ClientSupplier
    title = "Klijenti"
    headers = ["Naziv", "Email", "Telefon", "Status"]
    create_url_name = "client_app:client_create"

    def get_queryset(self):
        return super().get_queryset().order_by("name")

    def get_search_filter(self, query):
        return Q(name__icontains=query) | Q(email__icontains=query)


class BaseModelView(SuccessMessageMixin):
    template_name = "client_app/form_view.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        if hasattr(self, "log_activity"):
            self.log_activity()
        return response


class ClientCreateView(BaseModelView, CreateView):
    model = ClientSupplier
    form_class = ClientSupplierForm
    success_url = reverse_lazy("client_app:client_list")
    success_message = "Klijent uspješno kreiran"

    def log_activity(self):
        log_client_activity(self.object, "Client created.")


class ClientUpdateView(BaseModelView, UpdateView):
    model = ClientSupplier
    form_class = ClientSupplierForm
    success_url = reverse_lazy("client_app:client_list")
    success_message = "Klijent uspješno ažuriran"

    def log_activity(self):
        log_client_activity(self.object, "Client details updated.")


class ClientDeleteView(DeleteView):
    model = ClientSupplier
    success_url = reverse_lazy("client_app:client_list")
    template_name = "client_app/confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        log_client_activity(obj, "Client deleted.")
        return super().delete(request, *args, **kwargs)


class InvoiceListView(BaseListView):
    """Only displays invoices in CRM context - no create/edit functionality"""

    model = Invoice
    title = "Računi"
    headers = ["Broj računa", "Klijent", "Datum", "Status"]
    template_name = "client_app/list_view.html"
    create_url_name = "financije:invoice_create"

    def get_queryset(self):
        return Invoice.objects.select_related("client").order_by("-issue_date")

    def get_search_filter(self, query):
        return Q(invoice_number__icontains=query) | Q(client__name__icontains=query)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def opportunity_status_api(request, opportunity_id):
    try:
        opportunity = SalesOpportunity.objects.select_related("client").get(pk=opportunity_id)
        data = {
            "opportunity_id": opportunity.id,
            "client_name": opportunity.client.name if opportunity.client else "",
            "opportunity_name": opportunity.name,
            "status": opportunity.stage,
        }
        return JsonResponse(data)
    except (SalesOpportunity.DoesNotExist, ValidationError) as e:
        logger.error(f"Error fetching opportunity {opportunity_id}: {str(e)}")
        return JsonResponse({"error": str(e)}, status=404)


def lead_conversion_report(request):
    opportunities = SalesOpportunity.objects.all().values("stage", "created_at")
    df = pd.DataFrame(opportunities)

    if not df.empty:
        conversion_summary = df["stage"].value_counts().to_dict()
    else:
        conversion_summary = {}

    return JsonResponse({"lead_conversion_summary": conversion_summary})


def client_app_home(request):
    """Home view za CRM modul"""
    today = timezone.now().date()

    context = {
        "recent_clients": ClientSupplier.objects.filter(is_supplier=False).order_by("-date_created")[:5],
        "recent_activities": ClientActivityLog.objects.select_related("client").order_by("-timestamp")[:10],
        # Statistika
        "client_count": ClientSupplier.objects.filter(is_supplier=False).count(),
        "active_opportunities": SalesOpportunity.objects.filter(stage__in=["active", "negotiation"]).count(),
        "open_invoices": Invoice.objects.filter(
            status_fakture="open"  # Izmijenjeno iz status u status_fakture
        ).count(),
        "today_activities": ClientActivityLog.objects.filter(timestamp__date=today).count(),
    }
    return render(request, "client_app/index.html", context)


class ClientListCreateAPIView(generics.ListCreateAPIView):
    queryset = ClientSupplier.objects.all()
    serializer_class = ClientSupplierSerializer


class ClientRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ClientSupplier.objects.all()
    serializer_class = ClientSupplierSerializer


class SalesOrderListCreateAPIView(generics.ListCreateAPIView):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer  # Ensure SalesOrderSerializer is defined for SalesOrder


class SalesOrderRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer


class ClientSupplierViewSet(viewsets.ModelViewSet):
    queryset = ClientSupplier.objects.all()
    serializer_class = ClientSupplierSerializer


class SalesOpportunityViewSet(viewsets.ModelViewSet):
    queryset = SalesOpportunity.objects.all()
    serializer_class = SalesOpportunitySerializer


class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer


class SalesOrderViewSet(viewsets.ModelViewSet):
    queryset = SalesOrder.objects.all()
    serializer_class = SalesOrderSerializer


class ClientActivityLogViewSet(viewsets.ModelViewSet):
    queryset = ClientActivityLog.objects.all()
    serializer_class = ClientActivityLogSerializer


class OpportunityCreateView(BaseModelView, CreateView):
    model = SalesOpportunity
    form_class = SalesOpportunityForm
    success_url = reverse_lazy("client_app:opportunity_list")
    success_message = "Prodajna prilika uspješno kreirana"

    def form_valid(self, form):
        form.instance.created_at = timezone.now()
        response = super().form_valid(form)
        if self.object.client:
            log_client_activity(
                self.object.client,
                f"Kreirana prodajna prilika: {self.object.name}",
                "create",
            )
        return response


class OpportunityUpdateView(BaseModelView, UpdateView):
    model = SalesOpportunity
    form_class = SalesOpportunityForm
    success_url = reverse_lazy("client_app:opportunity_list")
    success_message = "Prodajna prilika ažurirana"

    def log_activity(self):
        if self.object.client:
            log_client_activity(
                self.object.client,
                f"Ažurirana prodajna prilika: {self.object.name}",
                "update",
            )


class OpportunityDeleteView(DeleteView):
    model = SalesOpportunity
    success_url = reverse_lazy("client_app:opportunity_list")
    template_name = "client_app/generic_confirm_delete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_name"] = self.object.name
        context["cancel_url"] = reverse_lazy("client_app:opportunity_list")
        return context

    def delete(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.client:
            log_client_activity(obj.client, f"Obrisana prodajna prilika: {obj.name}", "delete")
        return super().delete(request, *args, **kwargs)


def opportunity_list(request):
    query = request.GET.get("q")
    opportunities = SalesOpportunity.objects.select_related("client").order_by("-created_at")

    if query:
        opportunities = opportunities.filter(
            Q(name__icontains=query) | Q(client__name__icontains=query) | Q(stage__icontains=query)
        )

    paginator = Paginator(opportunities, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "title": "Prodajne prilike",
        "headers": ["Naziv", "Klijent", "Status", "Vrijednost"],
        "create_url": reverse_lazy("client_app:opportunity_create"),
    }
    return render(request, "client_app/list_view.html", context)
