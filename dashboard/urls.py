from django.urls import path

from . import views
from .views import break_even_dashboard, kpi_board

urlpatterns = [
    path("", views.dashboard_view, name="dashboard"),
    path("data/", views.dashboard_data, name="dashboard_data"),
    path("break-even/", break_even_dashboard, name="break_even_dashboard"),
    path("kpi-board/", kpi_board, name="kpi_board"),
]
