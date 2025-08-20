from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views import View
from rest_framework import viewsets

# ...existing imports...
from proizvodnja.models import RadniNalog  # Updated import

from .forms import DepartmentForm, EmployeeForm, RadnaEvaluacijaForm
from .models import (
    Department,
    Employee,
    ExpertiseLevel,
    HierarchicalLevel,
    Position,
    RadnaEvaluacija,
)
from .serializers import (
    DepartmentSerializer,
    EmployeeSerializer,
    ExpertiseLevelSerializer,
    HierarchicalLevelSerializer,
    PositionSerializer,
)


def index(request):
    return render(request, "ljudski_resursi/index.html")


def hr_view(request):
    # ...existing code...
    radni_nalozi = RadniNalog.objects.filter(employee=request.user)
    # ...existing code...


@login_required
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, "ljudski_resursi/employee_list.html", {"employees": employees})


@login_required
def employee_form(request, pk=None):
    if pk:
        employee = get_object_or_404(Employee, pk=pk)
        form_title = _("Update Employee")
    else:
        employee = None
        form_title = _("Create Employee")

    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, _("Employee successfully saved."))
            return redirect("ljudski_resursi:employee_list")
    else:
        form = EmployeeForm(instance=employee)

    return render(
        request,
        "ljudski_resursi/employee_form.html",
        {"form": form, "form_title": form_title, "employee": employee},
    )


@login_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == "POST":
        employee.delete()
        messages.success(request, _("Employee successfully deleted."))
        return redirect("ljudski_resursi:employee_list")
    return render(request, "ljudski_resursi/employee_confirm_delete.html", {"employee": employee})


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer


class ExpertiseLevelViewSet(viewsets.ModelViewSet):
    queryset = ExpertiseLevel.objects.all()
    serializer_class = ExpertiseLevelSerializer


class HierarchicalLevelViewSet(viewsets.ModelViewSet):
    queryset = HierarchicalLevel.objects.all()
    serializer_class = HierarchicalLevelSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer


class EmployeeCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = EmployeeForm()
        return render(request, "ljudski_resursi/employee_form.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("employee_list")
        return render(request, "ljudski_resursi/employee_form.html", {"form": form})


# Example of lazy import within a method to prevent circular dependency
def some_view(request):

    # ...use SomeModel as needed...
    return render(request, "some_template.html", {})


@login_required
def create_employee(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("employee_list")
    else:
        form = EmployeeForm()
    return render(request, "ljudski_resursi/create_employee.html", {"form": form})


class DepartmentCreateView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = DepartmentForm()
        return render(request, "ljudski_resursi/department_form.html", {"form": form})

    def post(self, request, *args, **kwargs):
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("department_list")
        return render(request, "ljudski_resursi/department_form.html", {"form": form})


@login_required
def department_list(request):
    departments = Department.objects.all()
    return render(request, "ljudski_resursi/department_list.html", {"departments": departments})


@login_required
def department_create(request):
    if request.method == "POST":
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Department successfully added."))
            return redirect("ljudski_resursi:department_list")
    else:
        form = DepartmentForm()
    return render(request, "ljudski_resursi/department_form.html", {"form": form})


def home(request):
    return render(request, "ljudski_resursi/home.html")


def position_list(request):
    positions = Position.objects.all()
    return render(request, "ljudski_resursi/position_list.html", {"positions": positions})


# ...other views...


@login_required
def evaluacija_list(request):
    evaluacije = RadnaEvaluacija.objects.all()
    return render(request, "ljudski_resursi/evaluacija_list.html", {"evaluacije": evaluacije})


@login_required
def evaluacija_create(request):
    if request.method == "POST":
        form = RadnaEvaluacijaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _("Evaluation successfully created."))
            return redirect("ljudski_resursi:evaluacija_list")
    else:
        form = RadnaEvaluacijaForm()
    return render(request, "ljudski_resursi/evaluacija_form.html", {"form": form})


@login_required
def evaluacija_update(request, pk):
    evaluacija = get_object_or_404(RadnaEvaluacija, pk=pk)
    if request.method == "POST":
        form = RadnaEvaluacijaForm(request.POST, instance=evaluacija)
        if form.is_valid():
            form.save()
            messages.success(request, _("Evaluation successfully updated."))
            return redirect("ljudski_resursi:evaluacija_list")
    else:
        form = RadnaEvaluacijaForm(instance=evaluacija)
    return render(
        request,
        "ljudski_resursi/evaluacija_form.html",
        {"form": form, "evaluacija": evaluacija},
    )


@login_required
def evaluacija_delete(request, pk):
    evaluacija = get_object_or_404(RadnaEvaluacija, pk=pk)
    if request.method == "POST":
        evaluacija.delete()
        messages.success(request, _("Evaluation successfully deleted."))
        return redirect("ljudski_resursi:evaluacija_list")
    return render(
        request,
        "ljudski_resursi/evaluacija_confirm_delete.html",
        {"evaluacija": evaluacija},
    )
