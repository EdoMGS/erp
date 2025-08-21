from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import TehnickaDokumentacijaForm
from .models import Projekt, RadniNalog, TehnickaDokumentacija
from .utils import log_action


# -------- 1. Lista tehničke dokumentacije -------- #
class ListaTehnickeDokumentacijeView(LoginRequiredMixin, ListView):
    model = TehnickaDokumentacija
    template_name = "lista_tehnicke_dokumentacije.html"
    context_object_name = "dokumentacija"
    paginate_by = 10

    def get_queryset(self):
        """
        Dohvaća tehničku dokumentaciju prema radnom nalogu ili projektu.
        """
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
        """
        Dodaje radni nalog ili projekt u kontekst, ako je primjenjivo.
        """
        context = super().get_context_data(**kwargs)
        context["radni_nalog"] = None
        context["projekt"] = None

        if "radni_nalog_id" in self.kwargs:
            context["radni_nalog"] = get_object_or_404(RadniNalog, id=self.kwargs["radni_nalog_id"])
        elif "projekt_id" in self.kwargs:
            context["projekt"] = get_object_or_404(Projekt, id=self.kwargs["projekt_id"])

        return context


# -------- 2. Detalji tehničke dokumentacije -------- #
class DetaljiTehnickeDokumentacijeView(LoginRequiredMixin, DetailView):
    model = TehnickaDokumentacija
    template_name = "detalji_tehnicke_dokumentacije.html"
    context_object_name = "dokumentacija"


# -------- 3. Dodavanje tehničke dokumentacije -------- #
class DodajTehnickuDokumentacijuView(LoginRequiredMixin, CreateView):
    model = TehnickaDokumentacija
    form_class = TehnickaDokumentacijaForm
    template_name = "dodaj_tehnicku_dokumentaciju.html"

    def form_valid(self, form):
        instance = form.save(commit=False)
        radni_nalog_id = self.kwargs.get("radni_nalog_id")
        projekt_id = self.kwargs.get("projekt_id")
        if radni_nalog_id:
            instance.radni_nalog = get_object_or_404(RadniNalog, id=radni_nalog_id)
        elif projekt_id:
            instance.projekt = get_object_or_404(Projekt, id=projekt_id)
        instance.save()
        form.save_m2m()
        try:
            from .utils import log_action

            log_action(self.request.user, instance, "CREATE", form.cleaned_data)
        except ImportError:
            pass
        messages.success(self.request, "Tehnička dokumentacija uspješno dodana!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        """
        Vraća korisnika na odgovarajuću listu dokumentacije.
        """
        if "radni_nalog_id" in self.kwargs:
            return reverse_lazy(
                "lista_tehnicke_dokumentacije",
                kwargs={"radni_nalog_id": self.kwargs["radni_nalog_id"]},
            )
        if "projekt_id" in self.kwargs:
            return reverse_lazy(
                "lista_tehnicke_dokumentacije",
                kwargs={"projekt_id": self.kwargs["projekt_id"]},
            )
        return reverse_lazy("lista_tehnicke_dokumentacije")


# -------- 4. Ažuriranje tehničke dokumentacije -------- #
class AzurirajTehnickuDokumentacijuView(LoginRequiredMixin, UpdateView):
    model = TehnickaDokumentacija
    form_class = TehnickaDokumentacijaForm
    template_name = "dodaj_tehnicku_dokumentaciju.html"

    def form_valid(self, form):
        """
        Sprema ažurirane podatke za tehničku dokumentaciju.
        """
        dokumentacija = form.save(commit=False)
        dokumentacija.save()
        form.save_m2m()

        # Logiranje ažuriranja
        log_action(self.request.user, dokumentacija, "UPDATE", form.cleaned_data)

        messages.success(self.request, "Tehnička dokumentacija uspješno ažurirana!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        """
        Vraća korisnika na detalje dokumentacije.
        """
        return reverse_lazy("detalji_tehnicke_dokumentacije", kwargs={"pk": self.object.pk})


# -------- 5. Brisanje tehničke dokumentacije -------- #
class ObrisiTehnickuDokumentacijuView(LoginRequiredMixin, DeleteView):
    model = TehnickaDokumentacija
    template_name = "obrisi_tehnicku_dokumentaciju.html"

    def delete(self, request, *args, **kwargs):
        """
        Implementira "soft delete" za tehničku dokumentaciju.
        """
        dokumentacija = self.get_object()
        dokumentacija.is_active = False
        dokumentacija.save()

        # Logiranje brisanja
        log_action(request.user, dokumentacija, "DELETE")

        messages.success(request, "Tehnička dokumentacija uspješno obrisana!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        """
        Vraća korisnika na odgovarajuću listu dokumentacije.
        """
        if "radni_nalog_id" in self.kwargs:
            return reverse_lazy(
                "lista_tehnicke_dokumentacije",
                kwargs={"radni_nalog_id": self.kwargs["radni_nalog_id"]},
            )
        if "projekt_id" in self.kwargs:
            return reverse_lazy(
                "lista_tehnicke_dokumentacije",
                kwargs={"projekt_id": self.kwargs["projekt_id"]},
            )
        return reverse_lazy("lista_tehnicke_dokumentacije")
