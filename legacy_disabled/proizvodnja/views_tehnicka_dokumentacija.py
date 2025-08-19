# proizvodnja/views_tehnicka_dokumentacija.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from projektiranje.forms import CADDocumentForm
from projektiranje.models import CADDocument

from .utils import informiraj_korisnika, log_action


# ==============================
# 1️⃣ Lista tehničke dokumentacije
# ==============================
class ListaTehnickeDokumentacijeView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = CADDocument
    template_name = "tehnicke_dokumentacije/lista_tehnicke_dokumentacije.html"
    context_object_name = "dokumentacije"
    paginate_by = 10

    def test_func(self):
        return self.request.user.groups.filter(name__in=["vlasnik", "direktor", "voditelj"]).exists()

    def get_queryset(self):
        queryset = CADDocument.objects.select_related("related_radni_nalog", "related_projekt").filter(is_active=True)
        radni_nalog_id = self.kwargs.get("radni_nalog_id")
        projekt_id = self.kwargs.get("projekt_id")

        if radni_nalog_id:
            queryset = queryset.filter(related_radni_nalog_id=radni_nalog_id)
        elif projekt_id:
            queryset = queryset.filter(related_projekt_id=projekt_id)

        return queryset.order_by("-uploaded_at")


# ==============================
# 2️⃣ Detalji tehničke dokumentacije
# ==============================
class DetaljiTehnickeDokumentacijeView(LoginRequiredMixin, DetailView):
    model = CADDocument
    template_name = "tehnicke_dokumentacije/detalji_tehnicke_dokumentacije.html"
    context_object_name = "dokumentacija"

    def get_queryset(self):
        return CADDocument.objects.filter(is_active=True).select_related("related_radni_nalog", "related_projekt")


# ==============================
# 3️⃣ Dodavanje tehničke dokumentacije
# ==============================
class DodajTehnickuDokumentacijuView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = CADDocument
    form_class = CADDocumentForm
    template_name = "tehnicke_dokumentacije/dodaj_tehnicku_dokumentaciju.html"

    def test_func(self):
        return self.request.user.groups.filter(name__in=["vlasnik", "direktor", "voditelj"]).exists()

    @transaction.atomic
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            dokumentacija = self.object
            log_action(self.request.user, dokumentacija, "CREATE", form.cleaned_data)
            informiraj_korisnika(dokumentacija)
            messages.success(self.request, "Tehnička dokumentacija uspješno dodana!")
            return response
        except Exception as e:
            messages.error(
                self.request,
                f"Greška prilikom dodavanja tehničke dokumentacije: {str(e)}",
            )
            return super().form_invalid(form)

    def get_success_url(self):
        radni_nalog_id = self.object.related_radni_nalog.id if hasattr(self.object, "related_radni_nalog") else None
        projekt_id = self.object.related_projekt.id if hasattr(self.object, "related_projekt") else None

        if radni_nalog_id:
            return reverse_lazy(
                "lista_tehnicke_dokumentacije",
                kwargs={"radni_nalog_id": radni_nalog_id},
            )
        if projekt_id:
            return reverse_lazy("lista_tehnicke_dokumentacije", kwargs={"projekt_id": projekt_id})
        return reverse_lazy("lista_tehnicke_dokumentacije")


# ==============================
# 4️⃣ Ažuriranje tehničke dokumentacije
# ==============================
class AzurirajTehnickuDokumentacijuView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CADDocument
    form_class = CADDocumentForm
    template_name = "tehnicke_dokumentacije/dodaj_tehnicku_dokumentaciju.html"
    success_url = reverse_lazy("lista_tehnicke_dokumentacije")

    def test_func(self):
        return self.request.user.groups.filter(name__in=["vlasnik", "direktor", "voditelj"]).exists()

    @transaction.atomic
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            dokumentacija = self.object
            log_action(self.request.user, dokumentacija, "UPDATE", form.cleaned_data)
            informiraj_korisnika(dokumentacija)
            messages.success(self.request, "Tehnička dokumentacija uspješno ažurirana!")
            return response
        except Exception as e:
            messages.error(
                self.request,
                f"Greška prilikom ažuriranja tehničke dokumentacije: {str(e)}",
            )
            return super().form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Greška prilikom ažuriranja tehničke dokumentacije.")
        return super().form_invalid(form)


# ==============================
# 5️⃣ Brisanje tehničke dokumentacije
# ==============================
class ObrisiTehnickuDokumentacijuView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = CADDocument
    template_name = "tehnicke_dokumentacije/obrisi_tehnicku_dokumentaciju.html"

    def test_func(self):
        return self.request.user.groups.filter(name__in=["vlasnik", "direktor", "voditelj"]).exists()

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            dokumentacija = self.get_object()
            dokumentacija.is_active = False
            dokumentacija.save()
            log_action(request.user, dokumentacija, "DELETE")
            messages.success(request, "Tehnička dokumentacija uspješno obrisana!")
            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(request, f"Greška prilikom brisanja tehničke dokumentacije: {str(e)}")
            return redirect("lista_tehnicke_dokumentacije")

    def get_success_url(self):
        radni_nalog_id = self.object.related_radni_nalog.id if hasattr(self.object, "related_radni_nalog") else None
        projekt_id = self.object.related_projekt.id if hasattr(self.object, "related_projekt") else None

        if radni_nalog_id:
            return reverse_lazy(
                "lista_tehnicke_dokumentacije",
                kwargs={"radni_nalog_id": radni_nalog_id},
            )
        if projekt_id:
            return reverse_lazy("lista_tehnicke_dokumentacije", kwargs={"projekt_id": projekt_id})
        return reverse_lazy("lista_tehnicke_dokumentacije")
