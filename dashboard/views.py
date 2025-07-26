from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from financije.models import BreakEvenSnapshot
from job_costing.models import JobCost
from project_costing.models import LabourEntry, Project


def dashboard_view(request):
    return render(request, "dashboard/dashboard.html")


def dashboard_data(request):
    # Aggregate data for dashboard
    qs = JobCost.objects.all()
    data = [
        {
            "id": jc.id,
            "name": jc.name,
            "revenue": float(jc.total_cost),
            "cost_50": float(jc.cost_50),
            "owner_20": float(jc.owner_20),
            "workers_30": float(jc.workers_30),
            "kpi_status": "OK" if jc.is_paid else "PENDING",
        }
        for jc in qs
    ]
    return JsonResponse({"rows": data})


@login_required
def break_even_dashboard(request):
    tenant = request.user.tenant
    snapshots = BreakEvenSnapshot.objects.filter(tenant=tenant).order_by("-date", "division")
    return render(request, "dashboard/break_even_dashboard.html", {"snapshots": snapshots})


def kpi_board(request):
    projects = Project.objects.all()
    context = {
        "projects": projects,
    }
    return render(request, "dashboard/kpi_board.html", context)


def worker_dashboard(request):
    labour_entries = LabourEntry.objects.all()
    context = {
        "labour_entries": labour_entries,
    }
    return render(request, "dashboard/worker_dashboard.html", context)
