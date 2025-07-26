from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import LabourEntryForm
from .models import Project


@login_required
def worker_timer(request):
    if request.method == "POST":
        form = LabourEntryForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect("worker_timer")
    else:
        form = LabourEntryForm(user=request.user)
    projects = Project.objects.filter(tenant=request.user.tenant)
    return render(
        request,
        "project_costing/worker_timer.html",
        {"form": form, "projects": projects},
    )
