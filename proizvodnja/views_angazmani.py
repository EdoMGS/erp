# proizvodnja/views_angazmani.py

from django.shortcuts import get_object_or_404, redirect
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
)
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.db import transaction

# Ispravno importamo Angazman, RadniNalog iz proizvodnja.models
from .models import Angazman, RadniNalog
# Import Employee iz ljudski_resursi.models
from ljudski_resursi.models import Employee

from .forms import AngazmanForm, DodatniAngazmanForm
from .utils import log_action

# ==============================
# 1️⃣ Lista angažmana
# ==============================
class ListaAngazmanaView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Angazman
    template_name = 'proizvodnja/angazmani/lista_angazmana.html'  # Updated path
    context_object_name = 'angazmani'
    paginate_by = 10

    def test_func(self):
        # Samo vlasnik/direktor/voditelj?
        return self.request.user.groups.filter(name__in=['vlasnik', 'direktor', 'voditelj']).exists()

    def get_queryset(self):
        qs = Angazman.objects.select_related('radni_nalog', 'employee').filter(is_active=True)
        radni_nalog_id = self.kwargs.get('radni_nalog_id')
        if radni_nalog_id:
            qs = qs.filter(radni_nalog_id=radni_nalog_id)
        return qs.order_by('-created_at')


# ==============================
# 2️⃣ Dodavanje angažmana
# ==============================
class DodajAngazmanView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Angazman
    form_class = AngazmanForm
    template_name = 'dodaj_angazman.html'

    def test_func(self):
        return self.request.user.groups.filter(name__in=['vlasnik', 'direktor', 'voditelj']).exists()

    def form_valid(self, form):
        # Moguća prilagodba logike
        return super().form_valid(form)


# ==============================
# 3️⃣ Ažuriranje angažmana
# ==============================
class AzurirajAngazmanView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Angazman
    form_class = AngazmanForm
    template_name = 'dodaj_angazman.html'

    def test_func(self):
        return self.request.user.groups.filter(name__in=['vlasnik', 'direktor', 'voditelj']).exists()

    def form_valid(self, form):
        return super().form_valid(form)


# ==============================
# 4️⃣ Dodavanje dodatnog angažmana
# ==============================
class DodajDodatniAngazmanView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Angazman  # Ili DodatniAngazman?
    form_class = DodatniAngazmanForm
    template_name = 'dodaj_dodatni_angazman.html'

    def test_func(self):
        return self.request.user.groups.filter(name__in=['vlasnik', 'direktor', 'voditelj']).exists()

    def form_valid(self, form):
        return super().form_valid(form)


# ==============================
# 5️⃣ Brisanje angažmana
# ==============================
class ObrisiAngazmanView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Angazman
    template_name = 'obrisi_angazman.html'

    def test_func(self):
        return self.request.user.groups.filter(name__in=['vlasnik', 'direktor', 'voditelj']).exists()

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        angazman = self.get_object()
        angazman.is_active = False
        angazman.save()
        log_action(request.user, angazman, 'DELETE')
        messages.success(request, "Angažman uspješno obrisan!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        radni_nalog = self.object.radni_nalog
        if radni_nalog:
            return reverse_lazy('lista_angazmana', kwargs={'radni_nalog_id': radni_nalog.id})
        return reverse_lazy('lista_angazmana')


# ==============================
# 6️⃣ Detalji angažmana
# ==============================
class DetaljiAngazmanaView(LoginRequiredMixin, DetailView):
    model = Angazman
    template_name = 'proizvodnja/angazmani/detalji_angazmana.html'  # Updated path
    context_object_name = 'angazman'
