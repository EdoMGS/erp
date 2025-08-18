from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r"procurement-plans", views.ProcurementPlanViewSet)
router.register(r"procurement-requests", views.ProcurementRequestViewSet)
router.register(r"purchase-orders", views.PurchaseOrderViewSet)
router.register(r"purchase-order-lines", views.PurchaseOrderLineViewSet)  # Dodano za PurchaseOrderLine
router.register(r"dobavljaci", views.DobavljacViewSet)  # Dodano za Dobavljac
router.register(r"grupe-dobavljaca", views.GrupaDobavljacaViewSet)  # Dodano za GrupaDobavljaca

app_name = "nabava"

urlpatterns = [
    # Osnovni view-ovi
    path("", views.procurement_dashboard, name="dashboard"),
    # Purchase Orders putanje
    path("orders/", views.purchase_order_list, name="order_list"),
    path("orders/create/", views.purchase_order_create, name="order_create"),
    path("orders/<int:pk>/", views.purchase_order_detail, name="order_detail"),
    path(
        "orders/<int:pk>/add-line/",
        views.purchase_order_add_line,
        name="order_add_line",
    ),  # Nova putanja
    # Procurement Plans putanje
    path("plans/", views.procurement_plan_list, name="plan_list"),
    path("plans/create/", views.procurement_plan_create, name="plan_create"),
    path("plans/<int:pk>/", views.procurement_plan_detail, name="plan_detail"),
    # Dobavljači putanje
    path("dobavljaci/", views.dobavljac_list, name="dobavljac_list"),
    path("dobavljaci/create/", views.dobavljac_create, name="dobavljac_create"),
    path("dobavljaci/<int:pk>/", views.dobavljac_detail, name="dobavljac_detail"),
    path("dobavljaci/<int:pk>/edit/", views.dobavljac_edit, name="dobavljac_edit"),  # Nova putanja
    # Grupe dobavljača putanje
    path("grupe/", views.grupa_dobavljaca_list, name="grupa_list"),
    path("grupe/create/", views.grupa_dobavljaca_create, name="grupa_create"),
    path("grupe/<int:pk>/", views.grupa_dobavljaca_detail, name="grupa_detail"),  # Nova putanja
    # Narudžbenice (stari sustav) putanje
    path("narudzbenice/", views.narudzbenica_list, name="narudzbenica_list"),
    path("narudzbenice/create/", views.narudzbenica_create, name="narudzbenica_create"),
    path("narudzbenice/<int:pk>/", views.narudzbenica_detail, name="narudzbenica_detail"),
    path("narudzbenice/<int:pk>/stavke/add/", views.add_stavka, name="add_stavka"),
    # API putanje
    path("api/", include(router.urls)),
    path("api/orders/", views.PurchaseOrderListAPI.as_view(), name="api_order_list"),
    path("api/plans/", views.ProcurementPlanListAPI.as_view(), name="api_plan_list"),
]
