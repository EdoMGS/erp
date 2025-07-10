# nalozi/views_projekti.py

import logging

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import ProjektForm  # Pretpostavka da je ProjektForm u forms.py
from .models import Notifikacija, Projekt, RadniNalog, TemplateRadniNalog

logger = logging.getLogger(__name__)

# =============================
# 1🌟 Lista projekata
# =============================
class ListaProjekataView(LoginRequiredMixin, ListView):
    model = Projekt
    template_name = 'proizvodnja/lista_projekata.html'
    context_object_name = 'projekti'
    paginate_by = 10

    def get_queryset(self):
        queryset = Projekt.objects.filter(is_active=True).select_related('tip_projekta', 'tip_vozila')
        # Ažuriramo status svakog projekta prije prikaza
        for projekt in queryset:
            projekt.azuriraj_status()
            projekt.save()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Provjeravamo je li korisnik vlasnik ili direktor (radi prikaza dodatnih opcija)
        context['korisnik_je_vlasnik'] = self.request.user.groups.filter(name__in=['vlasnik', 'direktor']).exists()
        return context


# =============================
# 2🌟 Detalji projekta
# =============================
class DetaljiProjektaView(LoginRequiredMixin, DetailView):
    model = Projekt
    template_name = 'proizvodnja/detalji_projekta.html'
    context_object_name = 'projekt'

    def get_object(self, queryset=None):
        projekt = super().get_object(queryset)
        projekt.azuriraj_status()  # Ažuriraj status prilikom dohvaćanja detalja
        projekt.save()
        return projekt

    def get_queryset(self):
        return Projekt.objects.select_related('tip_projekta', 'tip_vozila').prefetch_related('radni_nalozi', 'dokumentacija')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projekt = self.get_object()
        context['radni_nalozi'] = projekt.radni_nalozi.filter(is_active=True)
        context['dokumentacija'] = projekt.dokumentacija.all()
        context['korisnik_je_vlasnik'] = self.request.user.groups.filter(name__in=['vlasnik', 'direktor']).exists()
        return context


# =============================
# 3🌟 Kreiranje projekta
# =============================
class KreirajProjektView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Projekt
    form_class = ProjektForm
    template_name = 'proizvodnja/dodaj_uredi_projekt.html'
    success_url = reverse_lazy('lista_projekata')

    def test_func(self):
        # Pristup imaju vlasnici, direktori i voditelji
        return self.request.user.groups.filter(name__in=['vlasnik', 'direktor', 'voditelj']).exists()

    def get_form_kwargs(self):
        # Prosljeđujemo user formi, ako nam treba za logiku u ProjektForm
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        projekt = self.object  # novokreirani projekt

        # Ako je checkbox 'ručni_unos_radnih_naloga' = False (dakle user ne želi ručni unos)
        if not projekt.ručni_unos_radnih_naloga:
            # Provjeravamo da je tip_projekta "Izrada novih vatrogasnih vozila"
            # ili neki drugi naziv po želji
            if projekt.tip_projekta and projekt.tip_projekta.naziv == "Izrada novih vatrogasnih vozila":
                # Dohvati sve template radne naloge za taj tip projekta
                template_nalozi = TemplateRadniNalog.objects.filter(
                    tip_projekta=projekt.tip_projekta
                ).order_by('sort_index')

                # Ako želiš razlikovati i po tipu vozila (npr. cisterna vs. tehničko vozilo),
                # možeš ovdje dodati filter(tip_vozila=projekt.tip_vozila)
                # U prvoj iteraciji to ostavimo ovako.

                # Kreiramo radne naloge iz šablone
                for tmpl in template_nalozi:
                    RadniNalog.objects.create(
                        projekt=projekt,
                        naziv_naloga=tmpl.naziv_naloga,
                        opis=tmpl.opis_naloga,
                        grupa_posla=tmpl.grupa_posla,
                        template_nalog=tmpl,
                        predvidjeno_vrijeme=tmpl.get_prosjecni_sati(),
                        status="OTVOREN",
                        postotak_napretka=0,
                        # Po želji i prioritet, datum_pocetka itd.
                    )

        # Ažuriramo status projekta
        projekt.azuriraj_status()
        projekt.save()

        messages.success(self.request, "Projekt uspješno kreiran!")
        return response


# =============================
# 4🌟 Ažuriranje projekta
# =============================
class AzurirajProjektView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Projekt
    form_class = ProjektForm
    template_name = 'proizvodnja/dodaj_uredi_projekt.html'
    success_url = reverse_lazy('lista_projekata')

    def test_func(self):
        # Pristup imaju vlasnici, direktori i voditelji
        return self.request.user.groups.filter(name__in=['vlasnik', 'direktor', 'voditelj']).exists()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        """
        Kod ažuriranja projekta ne generiramo automatski radne naloge,
        jer projekt već postoji. Ako želiš, možeš ovdje dodati opciju
        generiranja novih radnih naloga. 
        """
        try:
            response = super().form_valid(form)
            self.object.azuriraj_status()
            self.object.save()
            messages.success(self.request, "Projekt uspješno ažuriran!")
            return response
        except Exception as e:
            logger.error(f"Greška prilikom ažuriranja projekta: {e}")
            messages.error(self.request, f"Greška prilikom ažuriranja projekta: {str(e)}")
            return super().form_invalid(form)


# =============================
# 5🌟 Brisanje projekta (soft delete)
# =============================
class ObrisiProjektView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Projekt
    template_name = 'proizvodnja/obrisi_projekt.html'

    def test_func(self):
        # Samo vlasnik i direktor mogu brisati projekte
        return self.request.user.groups.filter(name__in=['vlasnik', 'direktor']).exists()

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        projekt = self.get_object()
        aktivni_nalozi = projekt.radni_nalozi.filter(is_active=True)
        if aktivni_nalozi.exists():
            messages.error(request, "Projekt ne možete obrisati jer sadrži aktivne radne naloge.")
            return redirect('detalji_projekta', pk=projekt.pk)

        # Soft delete radnih naloga
        aktivni_nalozi.update(is_active=False)

        # Soft delete projekta
        projekt.is_active = False
        projekt.save()

        messages.success(request, "Projekt i povezani radni nalozi uspješno obrisani!")
        return redirect(reverse_lazy('lista_projekata'))

def projekt_detail(request, pk):
    """
    View function for displaying project details.
    """
    projekt = get_object_or_404(Projekt, pk=pk, is_active=True)
    context = {
        'projekt': projekt,
        'radni_nalozi': projekt.radni_nalozi.filter(is_active=True),
        'dokumentacija': projekt.dokumentacija.all() if hasattr(projekt, 'dokumentacija') else [],
        'korisnik_je_vlasnik': request.user.groups.filter(name__in=['vlasnik', 'direktor']).exists()
    }
    return render(request, 'proizvodnja/projekt_detail.html', context)
