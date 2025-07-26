from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DetailView, ListView,
                                  TemplateView, UpdateView)
from rest_framework import viewsets
from rest_framework.generics import GenericAPIView, RetrieveAPIView

from .forms import BillOfMaterialsForm, DesignTaskForm
from .models import (BillOfMaterials, BOMItem, CADDocument, DesignRevision,
                     DesignSegment, DesignTask, DynamicPlan)
from .serializers import (BillOfMaterialsSerializer, BOMItemSerializer,
                          CADDocumentSerializer, DesignRevisionSerializer,
                          DesignSegmentSerializer, DesignTaskSerializer,
                          DynamicPlanSerializer)


class DesignTaskViewSet(viewsets.ModelViewSet):
    queryset = DesignTask.objects.all()
    serializer_class = DesignTaskSerializer


class DesignSegmentViewSet(viewsets.ModelViewSet):
    queryset = DesignSegment.objects.all()
    serializer_class = DesignSegmentSerializer


class DynamicPlanViewSet(viewsets.ModelViewSet):
    queryset = DynamicPlan.objects.all()
    serializer_class = DynamicPlanSerializer


class BillOfMaterialsViewSet(viewsets.ModelViewSet):
    queryset = BillOfMaterials.objects.all()
    serializer_class = BillOfMaterialsSerializer


class BOMItemViewSet(viewsets.ModelViewSet):
    queryset = BOMItem.objects.all()
    serializer_class = BOMItemSerializer


class CADDocumentViewSet(viewsets.ModelViewSet):
    queryset = CADDocument.objects.all()
    serializer_class = CADDocumentSerializer


class DesignRevisionViewSet(viewsets.ModelViewSet):
    queryset = DesignRevision.objects.all()
    serializer_class = DesignRevisionSerializer


class ProjektiranjeHomeView(TemplateView):
    template_name = "projektiranje_app/home.html"


def index(request):
    return render(request, "projektiranje_app/home.html")


def neki_view(request):
    # Remove radni_nalozi reference
    return render(request, "neki_template.html")


def design_task_view(request):
    """Updated to use CADDocument"""
    doks = CADDocument.objects.all()
    return render(request, "projektiranje_app/design_task_view.html", {"documents": doks})


def dokumentacija_projektiranja_view(request):
    """Updated to use CADDocument"""
    docs = CADDocument.objects.all()
    return render(
        request,
        "projektiranje_app/dokumentacija_projektiranja_list.html",
        {"docs": docs},
    )


# DesignTask Views
class DesignTaskListView(ListView):
    model = DesignTask
    template_name = "projektiranje_app/designtask_list.html"
    context_object_name = "design_tasks"


class DesignTaskDetailView(DetailView):
    model = DesignTask
    template_name = "projektiranje_app/designtask_detail.html"
    context_object_name = "designtask"


class DesignTaskCreateView(CreateView):
    model = DesignTask
    form_class = DesignTaskForm
    template_name = "projektiranje_app/designtask_form.html"
    success_url = reverse_lazy("projektiranje_app:designtask_list")


class DesignTaskUpdateView(UpdateView):
    model = DesignTask
    form_class = DesignTaskForm
    template_name = "projektiranje_app/designtask_form.html"
    success_url = reverse_lazy("projektiranje_app:designtask_list")


# BillOfMaterials Views
class BillOfMaterialsListView(ListView):
    model = BillOfMaterials
    template_name = "projektiranje_app/billofmaterials_list.html"
    context_object_name = "billofmaterials"


class BillOfMaterialsDetailView(DetailView):
    model = BillOfMaterials
    template_name = "projektiranje_app/billofmaterials_detail.html"
    context_object_name = "billofmaterials"


class BillOfMaterialsCreateView(CreateView):
    model = BillOfMaterials
    form_class = BillOfMaterialsForm
    template_name = "projektiranje_app/billofmaterials_form.html"
    success_url = reverse_lazy("projektiranje_app:billofmaterials_list")


class BillOfMaterialsUpdateView(UpdateView):
    model = BillOfMaterials
    form_class = BillOfMaterialsForm
    template_name = "projektiranje_app/billofmaterials_form.html"
    success_url = reverse_lazy("projektiranje_app:billofmaterials_list")


# Update serializer usage in views
class SomeView(GenericAPIView):
    serializer_class = CADDocumentSerializer


class CADDocumentListCreateView(GenericAPIView):
    """Renamed from DokumentacijaProjektiranjaView"""

    queryset = CADDocument.objects.all()
    serializer_class = CADDocumentSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CADDocumentDetailView(RetrieveAPIView):
    """Renamed from DetaljiDokumentacijaProjektiranjaView"""

    queryset = CADDocument.objects.all()
    serializer_class = CADDocumentSerializer


# ...existing code...
