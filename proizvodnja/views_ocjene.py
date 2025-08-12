# proizvodnja/views_ocjene.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from proizvodnja.models import OcjenaKvalitete

from .forms import OcjenaKvaliteteForm
from .utils import informiraj_ocjenjivace, log_action


# ==============================
# 1️⃣ Lista ocjena kvalitete
# ==============================
class ListaOcjenaKvaliteteView(LoginRequiredMixin, ListView):
    model = OcjenaKvalitete
    template_name = "proizvodnja/ocjene/lista_ocjena.html"
    context_object_name = "ocjene"

    def get_queryset(self):
        qs = OcjenaKvalitete.objects.select_related("radni_nalog", "ocjenjivac").filter(is_active=True)

        # Filter by radni nalog if specified
        nalog_id = self.kwargs.get("radni_nalog_id")
        if nalog_id:
            qs = qs.filter(radni_nalog_id=nalog_id)

        return qs.order_by("-datum_ocjene")


# ==============================
# 2️⃣ Detalji ocjene kvalitete
# ==============================
class DetaljiOcjeneKvaliteteView(LoginRequiredMixin, DetailView):
    model = OcjenaKvalitete
    template_name = "proizvodnja/ocjene_kvalitete/detalji_ocjena_kvalitete.html"
    context_object_name = "ocjena_kvalitete"

    def get_queryset(self):
        return OcjenaKvalitete.objects.filter(is_active=True).select_related("radni_nalog", "employee")


# ==============================
# 3️⃣ Dodavanje ocjena
# ==============================
class DodajOcjenuView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = OcjenaKvalitete
    form_class = OcjenaKvaliteteForm
    template_name = "ocjene_kvalitete/dodaj_ocjenu_kvalitete.html"

    def test_func(self):
        return self.request.user.groups.filter(name__in=["direktor", "voditelj", "administrativno osoblje"]).exists()

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        ocjena = self.object

        log_action(self.request.user, ocjena, "CREATE", form.cleaned_data)
        informiraj_ocjenjivace(ocjena.radni_nalog)

        messages.success(self.request, "Ocjena kvalitete uspješno dodana!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Greška prilikom dodavanja ocjene.")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy("lista_ocjena_kvalitete")


# ==============================
# 4️⃣ Ažuriranje ocjena
# ==============================
class AzurirajOcjenuView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = OcjenaKvalitete
    form_class = OcjenaKvaliteteForm
    template_name = "ocjene_kvalitete/dodaj_ocjenu_kvalitete.html"
    success_url = reverse_lazy("lista_ocjena_kvalitete")

    def test_func(self):
        ocjena = self.get_object()
        return self.request.user == ocjena.employee.user or self.request.user.groups.filter(name="direktor").exists()

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        ocjena = self.object

        log_action(self.request.user, ocjena, "UPDATE", form.cleaned_data)
        informiraj_ocjenjivace(ocjena.radni_nalog)

        messages.success(self.request, "Ocjena kvalitete uspješno ažurirana!")
        return response

    def form_invalid(self, form):
        messages.error(self.request, "Greška prilikom ažuriranja ocjene.")
        return super().form_invalid(form)


# ==============================
# 5️⃣ Brisanje ocjena
# ==============================
class ObrisiOcjenuView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = OcjenaKvalitete
    template_name = "ocjene_kvalitete/obrisi_ocjenu_kvalitete.html"

    def test_func(self):
        ocjena = self.get_object()
        return self.request.user == ocjena.employee.user or self.request.user.groups.filter(name="direktor").exists()

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        ocjena = self.get_object()

        if not self.test_func():
            messages.error(request, "Nemate pravo obrisati ovu ocjenu.")
            return redirect("lista_ocjena_kvalitete")

        try:
            ocjena.is_active = False
            ocjena.save()

            log_action(request.user, ocjena, "DELETE")

            messages.success(request, "Ocjena kvalitete uspješno obrisana!")
            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(request, f"Greška prilikom brisanja ocjene: {str(e)}")
            return redirect("lista_ocjena_kvalitete")

    def get_success_url(self):
        return reverse_lazy("lista_ocjena_kvalitete")
