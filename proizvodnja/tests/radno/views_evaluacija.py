from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Sum
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .forms import (
    EvaluacijaProjektaForm,
    EvaluacijaRadnikaForm,
    EvaluacijaRadnogNalogaForm,
)
from .models import Projekt, RadniNalog, Zaposlenik
from .utils import log_action


# -------- 1. Evaluacija radnika -------- #
class EvaluacijaRadnikaView(LoginRequiredMixin, ListView):
    model = Zaposlenik
    template_name = "evaluacije/evaluacija_radnika.html"
    context_object_name = "radnici"
    paginate_by = 10

    def get_queryset(self):
        return Zaposlenik.objects.filter(is_active=True).annotate(
            prosjek_ocjena=Avg("ocjene_kvalitete__ocjena"),
            ukupno_sati=Sum("angazmani__sati_rada"),
        )


class DodajEvaluacijuRadnikaView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    form_class = EvaluacijaRadnikaForm
    template_name = "evaluacije/dodaj_evaluaciju_radnika.html"
    success_url = reverse_lazy("evaluacija_radnika")

    def test_func(self):
        return self.request.user.role in ["Direktor", "Voditelj Proizvodnje"]

    def form_valid(self, form):
        evaluacija = form.save()
        log_action(self.request.user, evaluacija, "CREATE")
        messages.success(
            self.request,
            f"Evaluacija za radnika {evaluacija.zaposlenik} uspješno dodana!",
        )
        return super().form_valid(form)


# -------- 2. Evaluacija projekata -------- #
class EvaluacijaProjektaView(LoginRequiredMixin, ListView):
    model = Projekt
    template_name = "evaluacije/evaluacija_projekta.html"
    context_object_name = "projekti"
    paginate_by = 10

    def get_queryset(self):
        return Projekt.objects.filter(is_active=True).annotate(
            prosjek_ocjena=Avg("radni_nalozi__ocjene_kvalitete__ocjena"),
            ukupno_radnih_naloga=Sum("radni_nalozi__id"),
        )


class DodajEvaluacijuProjektaView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    form_class = EvaluacijaProjektaForm
    template_name = "evaluacije/dodaj_evaluaciju_projekta.html"
    success_url = reverse_lazy("evaluacija_projekta")

    def test_func(self):
        return self.request.user.role in ["Direktor"]

    def form_valid(self, form):
        evaluacija = form.save()
        log_action(self.request.user, evaluacija, "CREATE")
        messages.success(self.request, f"Evaluacija za projekt {evaluacija.projekt} uspješno dodana!")
        return super().form_valid(form)


# -------- 3. Evaluacija radnih naloga -------- #
class EvaluacijaRadnogNalogaView(LoginRequiredMixin, ListView):
    model = RadniNalog
    template_name = "evaluacije/evaluacija_radnog_naloga.html"
    context_object_name = "radni_nalozi"
    paginate_by = 10

    def get_queryset(self):
        return RadniNalog.objects.filter(is_active=True).annotate(
            prosjek_ocjena=Avg("ocjene_kvalitete__ocjena"),
            ukupno_sati=Sum("angazmani__sati_rada"),
        )


class DodajEvaluacijuRadnogNalogaView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    form_class = EvaluacijaRadnogNalogaForm
    template_name = "evaluacije/dodaj_evaluaciju_radnog_naloga.html"
    success_url = reverse_lazy("evaluacija_radnog_naloga")

    def test_func(self):
        return self.request.user.role in ["Voditelj Proizvodnje"]

    def form_valid(self, form):
        evaluacija = form.save()
        log_action(self.request.user, evaluacija, "CREATE")
        messages.success(
            self.request,
            f"Evaluacija za radni nalog {evaluacija.radni_nalog} uspješno dodana!",
        )
        return super().form_valid(form)


# -------- 4. Generiranje izvještaja -------- #
class GenerirajIzvjestajView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    template_name = "evaluacije/izvjestaj.html"

    def test_func(self):
        return self.request.user.role in ["Direktor"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["izvjestaj_radnika"] = Zaposlenik.objects.filter(is_active=True).annotate(
            prosjek_ocjena=Avg("ocjene_kvalitete__ocjena"),
            ukupno_sati=Sum("angazmani__sati_rada"),
        )
        context["izvjestaj_radnih_naloga"] = RadniNalog.objects.filter(is_active=True).annotate(
            prosjek_ocjena=Avg("ocjene_kvalitete__ocjena"),
            ukupno_sati=Sum("angazmani__sati_rada"),
        )
        return context
