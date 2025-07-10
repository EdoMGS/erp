# skladiste/views.py

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView
from rest_framework import viewsets

from .forms import ArtiklForm, PrimkaForm, PrimkaStavkaForm
from .models import (Alat, Artikl, DnevnikDogadaja, HTZOprema, Izdatnica,
                     Lokacija, Materijal, Primka, PrimkaStavka,
                     SkladisteResurs, Zona)
from .serializers import (AlatSerializer, ArtiklSerializer,
                          DnevnikDogadajaSerializer, HTZOpremaSerializer,
                          LokacijaSerializer, MaterijalSerializer,
                          SkladisteResursSerializer, ZonaSerializer)


########################################
# 1) ViewSet za Zona
########################################
class ZonaViewSet(viewsets.ModelViewSet):
    queryset = Zona.objects.all()
    serializer_class = ZonaSerializer


########################################
# 2) ViewSet za Lokacija
########################################
class LokacijaViewSet(viewsets.ModelViewSet):
    queryset = Lokacija.objects.select_related("zona").all()
    serializer_class = LokacijaSerializer


########################################
# 3) ViewSet za Artikl
########################################
class ArtiklViewSet(viewsets.ModelViewSet):
    queryset = Artikl.objects.select_related("lokacija").all()
    serializer_class = ArtiklSerializer


########################################
# 4) ViewSet za SkladisteResurs
########################################
class SkladisteResursViewSet(viewsets.ModelViewSet):
    queryset = SkladisteResurs.objects.all()
    serializer_class = SkladisteResursSerializer


########################################
# 5) ViewSet za Materijal
########################################
class MaterijalViewSet(viewsets.ModelViewSet):
    """
    Materijal je vezan na radni_nalog (FK).
    Ako trebaš dodatne filtere, override-anom get_queryset ili dodaj filter_backends.
    """

    queryset = Materijal.objects.select_related("radni_nalog").all()
    serializer_class = MaterijalSerializer


########################################
# 6) ViewSet za Alat
########################################
class AlatViewSet(viewsets.ModelViewSet):
    queryset = Alat.objects.select_related("assigned_to").all()
    serializer_class = AlatSerializer


########################################
# 7) ViewSet za HTZOprema
########################################
class HTZOpremaViewSet(viewsets.ModelViewSet):
    queryset = HTZOprema.objects.select_related("assigned_to").all()
    serializer_class = HTZOpremaSerializer


########################################
# 8) ViewSet za DnevnikDogadaja
########################################
class DnevnikDogadajaViewSet(viewsets.ModelViewSet):
    queryset = DnevnikDogadaja.objects.select_related("artikl").all()
    serializer_class = DnevnikDogadajaSerializer


########################################
# 9) Inventory Management Views
########################################
@login_required
def inventory_list(request):
    """Pregled skladišta."""
    artikli = Artikl.objects.all()
    materijali = Materijal.objects.select_related("artikl", "radni_nalog").all()
    return render(
        request,
        "skladiste/inventory_list.html",
        {"artikli": artikli, "materijali": materijali, "title": "Pregled skladišta"},
    )


@login_required
def add_inventory_item(request):
    """Dodavanje novog artikla"""
    if request.method == "POST":
        form = ArtiklForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("inventory_list")
    else:
        form = ArtiklForm()
    return render(request, "skladiste/add_inventory_item.html", {"form": form})


@login_required
def artikl_list(request):
    artikli = Artikl.objects.select_related("lokacija").all()
    return render(request, "skladiste/artikl_list.html", {"artikli": artikli})


@login_required
def materijal_list(request):
    materijali = Materijal.objects.select_related("artikl", "radni_nalog").all()
    return render(request, "skladiste/materijal_list.html", {"materijali": materijali})


@login_required
def lista_artikala(request):
    artikli = Artikl.objects.filter(is_active=True)
    return render(request, "skladiste/lista_artikala.html", {"artikli": artikli})


@login_required
def detalji_artikla(request, pk):
    artikl = get_object_or_404(Artikl, pk=pk, is_active=True)
    return render(request, "skladiste/detalji_artikla.html", {"artikl": artikl})


@login_required
def primka_list(request):
    primke = Primka.objects.all().order_by("-datum")
    return render(request, "skladiste/primka_list.html", {"primke": primke})


@login_required
def primka_create(request):
    PrimkaStavkaFormSet = inlineformset_factory(
        Primka, PrimkaStavka, form=PrimkaStavkaForm, extra=1, can_delete=True
    )

    if request.method == "POST":
        form = PrimkaForm(request.POST)
        if form.is_valid():
            primka = form.save(commit=False)
            primka.created_by = request.user
            primka.save()

            formset = PrimkaStavkaFormSet(request.POST, instance=primka)
            if formset.is_valid():
                formset.save()
                # Update inventory quantities
                for stavka in primka.stavke.all():
                    artikl = stavka.artikl
                    artikl.trenutna_kolicina += stavka.kolicina
                    artikl.save()
                messages.success(request, "Primka je uspješno kreirana.")
                return redirect("primka_list")
    else:
        form = PrimkaForm()
        formset = PrimkaStavkaFormSet()

    return render(
        request, "skladiste/primka_form.html", {"form": form, "formset": formset}
    )


# List Views
class ZonaListView(ListView):
    model = Zona
    template_name = "skladiste/zona_list.html"
    context_object_name = "zone"


class LokacijaListView(ListView):
    model = Lokacija
    template_name = "skladiste/lokacija_list.html"
    context_object_name = "lokacije"


class ArtiklListView(ListView):
    model = Artikl
    template_name = "skladiste/artikl_list.html"
    context_object_name = "artikli"


class MaterijalListView(ListView):
    model = Materijal
    template_name = "skladiste/materijal_list.html"
    context_object_name = "materijali"


class PrimkaListView(ListView):
    model = Primka
    template_name = "skladiste/primka_list.html"
    context_object_name = "primke"


class IzdatnicaListView(ListView):
    model = Izdatnica
    template_name = "skladiste/izdatnica_list.html"
    context_object_name = "izdatnice"


# Detail Views
class ArtiklDetailView(DetailView):
    model = Artikl
    template_name = "skladiste/artikl_detail.html"
    context_object_name = "artikl"


class PrimkaDetailView(DetailView):
    model = Primka
    template_name = "skladiste/primka_detail.html"
    context_object_name = "primka"


class IzdatnicaDetailView(DetailView):
    model = Izdatnica
    template_name = "skladiste/izdatnica_detail.html"
    context_object_name = "izdatnica"


# Create Views
class ArtiklCreateView(CreateView):
    model = Artikl
    template_name = "skladiste/artikl_form.html"
    fields = [
        "naziv",
        "opis",
        "sifra",
        "jm",
        "min_kolicina",
        "trenutna_kolicina",
        "nabavna_cijena",
        "prodajna_cijena",
        "kategorija",
        "dobavljac",
        "lokacija",
    ]
    success_url = reverse_lazy("skladiste:artikl_list")


class PrimkaCreateView(CreateView):
    model = Primka
    template_name = "skladiste/primka_form.html"
    fields = ["broj_primke", "datum", "dobavljac", "napomena"]
    success_url = reverse_lazy("skladiste:primka_list")


class IzdatnicaCreateView(CreateView):
    model = Izdatnica
    template_name = "skladiste/izdatnica_form.html"
    fields = ["broj_izdatnice", "datum", "preuzeo", "napomena"]
    success_url = reverse_lazy("skladiste:izdatnica_list")


def alat_list(request):
    alati = Alat.objects.all()
    return render(request, "skladiste/alat_list.html", {"alati": alati})


def htz_oprema_list(request):
    oprema = HTZOprema.objects.all()
    return render(request, "skladiste/htz_oprema_list.html", {"oprema": oprema})
