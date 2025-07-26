# proizvodnja/views_evaluacija.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg, Count, Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView, View

# A Employee iz ljudski_resursi:
from ljudski_resursi.models import Employee
from ljudski_resursi.services import EvaluacijaService

# Ispravno importamo iz proizvodnja.models:
from .models import Projekt, RadniNalog


# ==============================
# 1️⃣ Evaluacija radnika
# ==============================
class EvaluacijaRadnikaView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Employee
    template_name = "evaluacije/evaluacija_radnika.html"
    context_object_name = "radnici"
    paginate_by = 10

    def test_func(self):
        # Primjer: samo vlasnik/direktor/voditelj
        return self.request.user.groups.filter(name__in=["vlasnik", "direktor", "voditelj"]).exists()

    def get_queryset(self):
        """
        Pretpostavka:
        - Employee ima is_active polje
        - Relation 'ocjene_kvalitete' s poljem 'ocjena' postoji
          (npr. OcjenaKvalitete.employee -> related_name='ocjene_kvalitete')
        - Relation 'angazmani' s poljem 'sati_rada' postoji
          (npr. Angazman.employee -> related_name='angazmani')
        """
        return Employee.objects.filter(is_active=True).annotate(
            prosjek_ocjena=Avg("ocjene_kvalitete__ocjena"),
            ukupno_sati=Sum("angazmani__sati_rada"),
        )


class RadnikEvaluacijaView(LoginRequiredMixin, View):
    def post(self, request, employee_id):
        employee = get_object_or_404(Employee, id=employee_id)
        period = request.POST.get("period")

        try:
            evaluacija = EvaluacijaService.kreiraj_evaluaciju(
                employee=employee, period=period, evaluator=request.user.employee
            )
            messages.success(request, "Evaluacija uspješno kreirana.")
        except Exception as e:
            messages.error(request, f"Greška pri kreiranju evaluacije: {str(e)}")

        return redirect("detalji_zaposlenika", pk=employee_id)


# ==============================
# 2️⃣ Evaluacija projekata
# ==============================
class EvaluacijaProjektaView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Projekt
    template_name = "evaluacije/evaluacija_projekta.html"
    context_object_name = "projekti"
    paginate_by = 10

    def test_func(self):
        return self.request.user.groups.filter(name__in=["vlasnik", "direktor"]).exists()

    def get_queryset(self):
        """
        Pretpostavka:
        - Projekt ima polje is_active=True
        - radni_nalozi -> OcjenaKvalitete -> ocjena
        - radni_nalozi -> related_name='radni_nalozi'
        """
        return Projekt.objects.filter(is_active=True).annotate(
            prosjek_ocjena=Avg("radni_nalozi__ocjene_kvalitete__ocjena"),
            ukupno_radnih_naloga=Count("radni_nalozi"),
        )


# ==============================
# 3️⃣ Generiranje izvještaja
# ==============================
class GenerirajIzvjestajView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = "evaluacije/izvjestaj.html"

    def test_func(self):
        return self.request.user.groups.filter(name__in=["vlasnik", "direktor"]).exists()

    def get(self, request, *args, **kwargs):
        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_context_data(self):
        """
        Primjer:
        - dohvaćamo radnike + prosjek ocjena + sumu sati.
        - dohvaćamo radne naloge + prosjek ocjena + sumu sati.
        """
        return {
            "izvjestaj_radnika": Employee.objects.filter(is_active=True).annotate(
                prosjek_ocjena=Avg("ocjene_kvalitete__ocjena"),
                ukupno_sati=Sum("angazmani__sati_rada"),
            ),
            "izvjestaj_radnih_naloga": RadniNalog.objects.filter(is_active=True).annotate(
                prosjek_ocjena=Avg("ocjene_kvalitete__ocjena"),
                ukupno_sati=Sum("angazmani__sati_rada"),
            ),
        }


# ==============================
# 4️⃣ Projekt Performance
# ==============================
class ProjektPerformanceView(LoginRequiredMixin, ListView):
    template_name = "proizvodnja/evaluacija/projekt_performance.html"
    model = Projekt

    def get_queryset(self):
        return Projekt.objects.annotate(
            avg_task_quality=Avg("radni_nalozi__ocjene_kvalitete__ocjena"),
            total_tasks=Count("radni_nalozi"),
            completed_tasks=Count("radni_nalozi", filter=Q(radni_nalozi__status="ZAVRSENO")),
        ).filter(is_active=True)


# ==============================
# 5️⃣ Radni Nalog Performance
# ==============================
class RadniNalogPerformanceView(LoginRequiredMixin, ListView):
    template_name = "proizvodnja/evaluacija/radni_nalog_performance.html"
    model = RadniNalog

    def get_queryset(self):
        return RadniNalog.objects.annotate(
            avg_quality=Avg("ocjene_kvalitete__ocjena"),
            total_hours=Sum("angazmani__sati_rada"),
        ).filter(is_active=True)
