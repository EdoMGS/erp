# erp_system/proizvodnja/urls.py

from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views
from .views_angazmani import (AzurirajAngazmanView, DetaljiAngazmanaView,
                              DodajAngazmanView, DodajDodatniAngazmanView,
                              ListaAngazmanaView, ObrisiAngazmanView)
from .views_dnevni_izvjestaj import (DnevniIzvjestajView,
                                     GenerirajPDFDnevniIzvjestajView)
from .views_ocjene import (AzurirajOcjenuView, DetaljiOcjeneKvaliteteView,
                           DodajOcjenuView, ListaOcjenaKvaliteteView,
                           ObrisiOcjenuView)
from .views_projekti import AzurirajProjektView  # Add this import
from .views_tehnicka_dokumentacija import (AzurirajTehnickuDokumentacijuView,
                                           DetaljiTehnickeDokumentacijeView,
                                           DodajTehnickuDokumentacijuView,
                                           ListaTehnickeDokumentacijeView,
                                           ObrisiTehnickuDokumentacijuView)
from .views_video import (AzurirajVideoMaterijalView, DodajVideoMaterijalView,
                          DodajVideoPitanjeView, ListaVideoMaterijalaView,
                          ListaVideoPitanjaView, ObrisiVideoMaterijalView,
                          ObrisiVideoPitanjeView)

# Ako želiš koristiti "protected_view", import ga iz utils
# from .utils import protected_view

# Hard-coded role lists - up to you if you want to keep them
TOP_MANAGEMENT = ["Direktor", "Administrator", "Vlasnik"]
MIDDLE_MANAGEMENT = [
    "Voditelj Projekta",
    "Voditelj Proizvodnje",
    "Nabava",
    "Projektant",
]
OPERATIVA = ["Radnik", "Skladištar"]
ALLOWED_MANAGEMENT = TOP_MANAGEMENT + MIDDLE_MANAGEMENT

app_name = "proizvodnja"

urlpatterns = [
    # Base views
    path("", views.proizvodnja_home, name="home"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("centralni-panel/", views.centralni_panel, name="centralni_panel"),
    # Dnevni izvještaji
    path(
        "dnevni-izvjestaj/",
        login_required(DnevniIzvjestajView.as_view()),
        name="dnevni_izvjestaj",
    ),
    path(
        "dnevni-izvjestaj/pdf/",
        login_required(GenerirajPDFDnevniIzvjestajView.as_view()),
        name="pdf_dnevni_izvjestaj",
    ),
    # Project related
    path("projekti/", views.lista_projekata, name="lista_projekata"),
    path("projekt/<int:pk>/", views.projekt_detail, name="projekt_detail"),
    path("projekt/add/", views.projekt_add, name="projekt_add"),
    path("projekt/<int:pk>/edit/", views.projekt_edit, name="projekt_edit"),
    # Work orders
    path(
        "projekt/<int:projekt_id>/radni-nalozi/",
        views.lista_radnih_naloga,
        name="lista_radnih_naloga",
    ),
    path("radni-nalog/<int:pk>/", views.radni_nalog_detail, name="radni_nalog_detail"),
    path("radni-nalog/add/", views.radni_nalog_add, name="radni_nalog_add"),
    path("radni-nalog/<int:pk>/edit/", views.radni_nalog_edit, name="radni_nalog_edit"),
    # Materials & resources
    path("materijali/", views.lista_materijala, name="lista_materijala"),
    path(
        "materijali/<int:radni_nalog_id>/",
        views.lista_materijala,
        name="lista_materijala_po_nalogu",
    ),
    # Engagement URLs
    path(
        "angazmani/",
        login_required(ListaAngazmanaView.as_view()),
        name="lista_angazmana",
    ),
    path(
        "angazman/dodaj/",
        login_required(DodajAngazmanView.as_view()),
        name="dodaj_angazman",
    ),
    path(
        "angazman/<int:pk>/",
        login_required(DetaljiAngazmanaView.as_view()),
        name="detalji_angazmana",
    ),
    path(
        "angazman/<int:pk>/azuriraj/",
        login_required(AzurirajAngazmanView.as_view()),
        name="azuriraj_angazman",
    ),
    path(
        "angazman/<int:pk>/obrisi/",
        login_required(ObrisiAngazmanView.as_view()),
        name="obrisi_angazman",
    ),
    path(
        "angazman/dodatni/dodaj/",
        login_required(DodajDodatniAngazmanView.as_view()),
        name="dodaj_dodatni_angazman",
    ),
    # Video materijali
    path(
        "video-materijali/",
        login_required(ListaVideoMaterijalaView.as_view()),
        name="lista_video_materijala",
    ),
    path(
        "video-materijali/dodaj/",
        login_required(DodajVideoMaterijalView.as_view()),
        name="dodaj_video_materijal",
    ),
    path(
        "video-materijali/<int:pk>/azuriraj/",
        login_required(AzurirajVideoMaterijalView.as_view()),
        name="azuriraj_video_materijal",
    ),
    path(
        "video-materijali/<int:pk>/obrisi/",
        login_required(ObrisiVideoMaterijalView.as_view()),
        name="obrisi_video_materijal",
    ),
    # Video pitanja
    path(
        "video-pitanja/",
        login_required(ListaVideoPitanjaView.as_view()),
        name="lista_video_pitanja",
    ),
    path(
        "video-pitanje/dodaj/",
        login_required(DodajVideoPitanjeView.as_view()),
        name="dodaj_video_pitanje",
    ),
    path(
        "video-pitanje/<int:pk>/obrisi/",
        login_required(ObrisiVideoPitanjeView.as_view()),
        name="obrisi_video_pitanje",
    ),
    # Quality evaluations
    path(
        "ocjene-kvalitete/<int:radni_nalog_id>/",
        login_required(ListaOcjenaKvaliteteView.as_view()),
        name="lista_ocjena_kvalitete",
    ),
    path(
        "ocjena-kvalitete/<int:pk>/",
        login_required(DetaljiOcjeneKvaliteteView.as_view()),
        name="detalji_ocjene_kvalitete",
    ),
    path(
        "ocjena-kvalitete/<int:pk>/edit/",
        login_required(AzurirajOcjenuView.as_view()),
        name="azuriraj_ocjenu_kvalitete",
    ),
    path(
        "ocjena-kvalitete/dodaj/",
        login_required(DodajOcjenuView.as_view()),
        name="dodaj_ocjenu_kvalitete",
    ),
    path(
        "ocjena-kvalitete/<int:pk>/obrisi/",
        login_required(ObrisiOcjenuView.as_view()),
        name="obrisi_ocjenu_kvalitete",
    ),
    # Universal work order form
    path(
        "radni-nalog/univerzalni/<str:action>/",
        views.univerzalni_radni_nalog,
        name="univerzalni_radni_nalog",
    ),
    path(
        "radni-nalog/univerzalni/<int:pk>/<str:action>/",
        views.univerzalni_radni_nalog,
        name="univerzalni_radni_nalog_edit",
    ),
    path(
        "radni-nalog/univerzalni/",
        views.univerzalni_radni_nalog,
        name="univerzalni_radni_nalog_new",
    ),
    path(
        "radni-nalog/univerzalni/<int:pk>/",
        views.univerzalni_radni_nalog,
        name="univerzalni_radni_nalog_edit",
    ),
    path(
        "radni-nalog/univerzalni/<int:pk>/view/",
        views.univerzalni_radni_nalog,
        {"action": "view"},
        name="univerzalni_radni_nalog_view",
    ),
    # Login
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="accounts/login.html"),
        name="login",
    ),
]

# Technical documentation URLs
urlpatterns += [
    path(
        "tehnicka-dokumentacija/",
        ListaTehnickeDokumentacijeView.as_view(),
        name="lista_tehnicke_dokumentacije",
    ),
    path(
        "tehnicka-dokumentacija/<int:pk>/",
        DetaljiTehnickeDokumentacijeView.as_view(),
        name="detalji_tehnicke_dokumentacije",
    ),
    path(
        "tehnicka-dokumentacija/dodaj/",
        DodajTehnickuDokumentacijuView.as_view(),
        name="dodaj_tehnicku_dokumentaciju",
    ),
    path(
        "tehnicka-dokumentacija/<int:pk>/azuriraj/",
        AzurirajTehnickuDokumentacijuView.as_view(),
        name="azuriraj_tehnicku_dokumentaciju",
    ),
    path(
        "tehnicka-dokumentacija/<int:pk>/obrisi/",
        ObrisiTehnickuDokumentacijuView.as_view(),
        name="obrisi_tehnicku_dokumentaciju",
    ),
]
