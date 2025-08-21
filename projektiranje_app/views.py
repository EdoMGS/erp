from django.views.generic import ListView
from rest_framework import viewsets

from .models import DesignTask
from .serializers import DesignTaskSerializer


class DesignTaskViewSet(viewsets.ModelViewSet):
    queryset = DesignTask.objects.all()
    serializer_class = DesignTaskSerializer


class DesignTaskListView(ListView):
    model = DesignTask
    template_name = "projektiranje_app/designtask_list.html"
    context_object_name = "design_tasks"


# Minimal set: only list view + API viewset for stub model. Other legacy
# views removed in stub configuration.
