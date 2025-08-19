from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import MaterijalForm
from .models import Materijal, Notifikacija, Projekt, RadniNalog
from .utils import informiraj_korisnika, log_action


# -------- 1. Lista materijala -------- #
class ListaMaterijalaView(LoginRequiredMixin, ListView):
    model = Materijal
    template_name = "lista_materijala.html"
    context_object_name = "materijali"
    paginate_by = 10

    def get_queryset(self):
        radni_nalog_id = self.kwargs.get("radni_nalog_id")
        projekt_id = self.kwargs.get("projekt_id")

        if radni_nalog_id:
            queryset = super().get_queryset().filter(radni_nalog_id=radni_nalog_id, is_active=True)
        elif projekt_id:
            queryset = super().get_queryset().filter(projekt_id=projekt_id, is_active=True)
        else:
            queryset = super().get_queryset().filter(is_active=True)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["radni_nalog"] = None
        context["projekt"] = None

        if "radni_nalog_id" in self.kwargs:
            context["radni_nalog"] = get_object_or_404(RadniNalog, id=self.kwargs["radni_nalog_id"])
        elif "projekt_id" in self.kwargs:
            context["projekt"] = get_object_or_404(Projekt, id=self.kwargs["projekt_id"])

        return context


# -------- 2. Detalji materijala -------- #
class DetaljiMaterijalaView(LoginRequiredMixin, DetailView):
    model = Materijal
    template_name = "detalji_materijala.html"
    context_object_name = "materijal"


# -------- 3. Dodavanje materijala -------- #
class DodajMaterijalView(LoginRequiredMixin, CreateView):
    model = Materijal
    form_class = MaterijalForm
    template_name = "dodaj_materijal.html"

    def form_valid(self, form):
        materijal = form.save(commit=False)
        radni_nalog_id = self.kwargs.get("radni_nalog_id")
        projekt_id = self.kwargs.get("projekt_id")

        if radni_nalog_id:
            materijal.radni_nalog = get_object_or_404(RadniNalog, id=radni_nalog_id)
        elif projekt_id:
            materijal.projekt = get_object_or_404(Projekt, id=projekt_id)

        materijal.save()

        log_action(self.request.user, materijal, "CREATE", form.cleaned_data)

        messages.success(self.request, "Materijal uspješno dodan!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        if "radni_nalog_id" in self.kwargs:
            return reverse_lazy(
                "lista_materijala",
                kwargs={"radni_nalog_id": self.kwargs["radni_nalog_id"]},
            )
        if "projekt_id" in self.kwargs:
            return reverse_lazy("lista_materijala", kwargs={"projekt_id": self.kwargs["projekt_id"]})
        return reverse_lazy("lista_materijala")


# -------- 4. Ažuriranje materijala -------- #
class AzurirajMaterijalView(LoginRequiredMixin, UpdateView):
    model = Materijal
    form_class = MaterijalForm
    template_name = "dodaj_materijal.html"

    def form_valid(self, form):
        materijal = form.save(commit=False)
        materijal.save()

        log_action(self.request.user, materijal, "UPDATE", form.cleaned_data)

        messages.success(self.request, "Materijal uspješno ažuriran!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("detalji_materijala", kwargs={"pk": self.object.pk})


# -------- 5. Brisanje materijala -------- #
class ObrisiMaterijalView(LoginRequiredMixin, DeleteView):
    model = Materijal
    template_name = "obrisi_materijal.html"

    def delete(self, request, *args, **kwargs):
        materijal = self.get_object()
        materijal.is_active = False
        materijal.save()

        log_action(request.user, materijal, "DELETE")

        messages.success(request, "Materijal uspješno obrisan!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        if "radni_nalog_id" in self.kwargs:
            return reverse_lazy(
                "lista_materijala",
                kwargs={"radni_nalog_id": self.kwargs["radni_nalog_id"]},
            )
        if "projekt_id" in self.kwargs:
            return reverse_lazy("lista_materijala", kwargs={"projekt_id": self.kwargs["projekt_id"]})
        return reverse_lazy("lista_materijala")


# -------- 6. Notifikacija za bypass materijala -------- #
def kreiraj_notifikaciju(radni_nalog, poruka):
    if radni_nalog.odgovorna_osoba:
        korisnik = radni_nalog.odgovorna_osoba.korisnik
        Notifikacija.objects.create(korisnik=korisnik, poruka=poruka)
        informiraj_korisnika(korisnik, poruka)
