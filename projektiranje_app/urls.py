from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (BillOfMaterialsViewSet, BOMItemViewSet, CADDocumentViewSet,
                    DesignRevisionViewSet, DesignSegmentViewSet,
                    DesignTaskCreateView, DesignTaskDetailView,
                    DesignTaskListView, DesignTaskUpdateView,
                    DesignTaskViewSet, DynamicPlanViewSet,
                    ProjektiranjeHomeView, index)

app_name = "projektiranje_app"

router = DefaultRouter()
router.register(r"design-tasks", DesignTaskViewSet)
router.register(r"design-segments", DesignSegmentViewSet)
router.register(r"dynamic-plans", DynamicPlanViewSet)
router.register(r"bill-of-materials", BillOfMaterialsViewSet)
router.register(r"bom-items", BOMItemViewSet)
router.register(r"cad-documents", CADDocumentViewSet)
router.register(r"design-revisions", DesignRevisionViewSet)

urlpatterns = [
    path("", index, name="home"),  # This is already correct
    path("api/", include(router.urls)),
    path(
        "projektiranje-home/",
        ProjektiranjeHomeView.as_view(),
        name="projektiranje-home",
    ),
    # Design Task URLs
    path("design-tasks/", DesignTaskListView.as_view(), name="designtask_list"),
    path(
        "design-tasks/<int:pk>/",
        DesignTaskDetailView.as_view(),
        name="designtask_detail",
    ),
    path("design-tasks/create/", DesignTaskCreateView.as_view(), name="designtask_create"),
    path(
        "design-tasks/<int:pk>/update/",
        DesignTaskUpdateView.as_view(),
        name="designtask_update",
    ),
]
