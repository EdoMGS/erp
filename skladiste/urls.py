# skladiste/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import (
    ZonaListView, LokacijaListView, ArtiklListView, MaterijalListView,
    ArtiklDetailView, ArtiklCreateView,
    PrimkaListView, PrimkaDetailView, PrimkaCreateView,
    IzdatnicaListView, IzdatnicaDetailView, IzdatnicaCreateView
)

app_name = 'skladiste'

# API Router
router = DefaultRouter()
router.register(r'zone', views.ZonaViewSet)
router.register(r'lokacije', views.LokacijaViewSet)
router.register(r'artikli-api', views.ArtiklViewSet)

urlpatterns = [
    # API URLs
    path('api/', include(router.urls)),

    # Main views
    path('', views.inventory_list, name='inventory_list'),
    
    # Artikl URLs
    path('artikli/', ArtiklListView.as_view(), name='artikl_list'),
    path('artikli/<int:pk>/', ArtiklDetailView.as_view(), name='artikl_detail'),
    path('artikli/create/', ArtiklCreateView.as_view(), name='artikl_create'),
    
    # Zona & Lokacija URLs
    path('zone/', ZonaListView.as_view(), name='zona_list'),
    path('lokacije/', LokacijaListView.as_view(), name='lokacija_list'),
    
    # Materijal URLs
    path('materijali/', MaterijalListView.as_view(), name='materijal_list'),
    
    # Primka URLs
    path('primke/', PrimkaListView.as_view(), name='primka_list'),
    path('primke/<int:pk>/', PrimkaDetailView.as_view(), name='primka_detail'),
    path('primke/create/', PrimkaCreateView.as_view(), name='primka_create'),
    
    # Izdatnica URLs
    path('izdatnice/', IzdatnicaListView.as_view(), name='izdatnica_list'),
    path('izdatnice/<int:pk>/', IzdatnicaDetailView.as_view(), name='izdatnica_detail'),
    path('izdatnice/create/', IzdatnicaCreateView.as_view(), name='izdatnica_create'),
    
    # Equipment URLs
    path('alati/', views.alat_list, name='alat_list'),
    path('htz-oprema/', views.htz_oprema_list, name='htz_oprema_list'),
]
