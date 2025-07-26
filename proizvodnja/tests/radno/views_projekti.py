from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import ProjektForm
from .models import Projekt


class ListaProjekataView(LoginRequiredMixin, ListView):
    model = Projekt
    template_name = "nalozi/lista_projekata.html"
    context_object_name = "projekti"
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True).order_by("-created_at")
        for projekt in queryset:
            projekt.azuriraj_status()  # Ažuriranje statusa
        return queryset


class DetaljiProjektaView(LoginRequiredMixin, DetailView):
    model = Projekt
    template_name = "detalji_projekta.html"
    context_object_name = "projekt"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projekt = self.get_object()
        context.update(
            {
                "radni_nalozi": projekt.radni_nalozi.filter(is_active=True),
                "dokumentacija": projekt.dokumentacija.all(),
                "tip_projekta_info": projekt.tip_projekta,
                "tip_vozila_info": projekt.tip_vozila,
            }
        )
        return context


class KreirajProjektView(LoginRequiredMixin, CreateView):
    model = Projekt
    form_class = ProjektForm
    template_name = "nalozi/dodaj_uredi_projekt.html"
    success_url = reverse_lazy("lista_projekata")

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.save()
        form.save_m2m()
        messages.success(self.request, "Projekt uspješno kreiran!")
        return super().form_valid(form)


class AzurirajProjektView(LoginRequiredMixin, UpdateView):
    model = Projekt
    form_class = ProjektForm
    template_name = "nalozi/dodaj_uredi_projekt.html"
    success_url = reverse_lazy("lista_projekata")

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.save()
        form.save_m2m()
        messages.success(self.request, "Projekt uspješno ažuriran!")
        return super().form_valid(form)


class ObrisiProjektView(LoginRequiredMixin, DeleteView):
    model = Projekt
    template_name = "obrisi_projekt.html"
    success_url = reverse_lazy("lista_projekata")

    def delete(self, request, *args, **kwargs):
        projekt = self.get_object()
        if projekt.radni_nalozi.filter(is_active=True).exists():
            messages.error(request, "Projekt se ne može obrisati jer ima aktivne radne naloge.")
            return redirect("detalji_projekta", pk=projekt.pk)

        projekt.is_active = False
        projekt.save()

        messages.success(request, "Projekt uspješno obrisan!")
        return redirect(self.success_url)
