from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import DesignTaskListView, DesignTaskViewSet

app_name = "projektiranje_app"

router = DefaultRouter()
router.register(r"design-tasks", DesignTaskViewSet)

urlpatterns = [
    path("api/", include(router.urls)),
    path("design-tasks/", DesignTaskListView.as_view(), name="designtask_list"),
]
