from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    ClientCreateView,
    ClientUpdateView,
    ClientDeleteView,
    OpportunityCreateView,
    OpportunityUpdateView,
    OpportunityDeleteView,
)

app_name = 'client_app'

# API Router setup
router = DefaultRouter()
router.register(r'clients', views.ClientSupplierViewSet)
router.register(r'opportunities', views.SalesOpportunityViewSet)
router.register(r'activities', views.ClientActivityLogViewSet)

urlpatterns = [
    # Main app views
    path('', views.client_app_home, name='home'),
    path('api/', include(router.urls)),

    # Client management
    path('clients/', views.ClientListView.as_view(), name='client_list'),
    path('clients/add/', ClientCreateView.as_view(), name='client_create'),
    path('clients/<int:pk>/', views.ClientUpdateView.as_view(), name='client_edit'),
    path('clients/<int:pk>/delete/', views.ClientDeleteView.as_view(), name='client_delete'),

    # Sales opportunities
    path('opportunities/', views.opportunity_list, name='opportunity_list'),
    path('opportunities/add/', OpportunityCreateView.as_view(), name='opportunity_create'),
    path('opportunities/<int:pk>/edit/', OpportunityUpdateView.as_view(), name='opportunity_edit'),
    path('opportunities/<int:pk>/delete/', OpportunityDeleteView.as_view(), name='opportunity_delete'),

    # Invoices - only list view
    path('invoices/', views.InvoiceListView.as_view(), name='invoice_list'),

    # API endpoints
    path('api/opportunity-status/<int:opportunity_id>/', 
         views.opportunity_status_api, 
         name='opportunity_status_api'),
    path('api/lead-conversion-report/', 
         views.lead_conversion_report, 
         name='lead_conversion_report'),
]