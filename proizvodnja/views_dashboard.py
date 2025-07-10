import json
from decimal import Decimal  # Moved to the top

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import View
from django.views.generic import ListView

from financije.services import calculate_project_costs
from ljudski_resursi.models import Employee
from skladiste.models import Materijal

from .models import (
    Angazman,
    GrupaPoslova,
    Notifikacija,
    PovijestPromjena,
    Projekt,
    RadniNalog,
)

# nalozi/views_dashboard.py


@login_required
def home_view(request):
    """Početna stranica."""
    context = {
        "user": request.user,
        "notifikacije_neprocitane": Notifikacija.objects.filter(
            korisnik=request.user, procitano=False
        ).count(),
    }
    return render(request, "nalozi/home.html", context)


class DashboardView(LoginRequiredMixin, View):
    template_name = "nalozi/dashboard.html"

    def get(self, request, *args, **kwargs):
        # Dohvaćamo parametre iz GET-a
        projekt_id = request.GET.get("projekt_id")
        radnik_id = request.GET.get("radnik_id")

        # Build kontekst ovisno o tome je li user superuser, direktor, radnik...
        user = request.user
        if user.is_superuser:
            context = self.get_director_context()
            context["is_superuser"] = True
        else:
            if hasattr(user, "employee"):
                employee = user.employee
                position_title = employee.position.title
                if position_title in ["Vlasnik", "Direktor"]:
                    context = self.get_director_context()
                    context["is_vlasnik_or_direktor"] = True
                elif position_title in ["Voditelj", "Administrator"]:
                    context = self.get_voditelj_context()
                    context["is_voditelj_or_admin"] = True
                else:
                    context = self.get_radnik_context(employee)
                    context["is_radnik"] = True
            else:
                context = {}
                context["is_unknown"] = True

        # DODAJEMO filtriranje po projektu i radniku u Gantt i popis
        # (kao i resursni “Workload chart”).
        radni_nalozi_qs = self.get_filtered_radni_nalozi(
            projekt_id, radnik_id
        ).select_related("projekt", "grupa_posla")
        context["radni_nalozi"] = radni_nalozi_qs

        # Generiraj Gantt Data
        gantt_data = self.get_gantt_data(radni_nalozi_qs)
        context["gantt_data_json"] = json.dumps(gantt_data, ensure_ascii=False)

        # Dodatne “financije i materijali”
        # (Pokazat ćemo ih ako je user menadžer/direktor)
        if (
            user.is_superuser
            or context.get("is_vlasnik_or_direktor")
            or context.get("is_voditelj_or_admin")
        ):
            fin_mat = self.get_financial_material_context()
            context.update(fin_mat)

        # Za workload chart – dohvat podataka o radnicima i zbroju sati
        context["workload_chart_data"] = json.dumps(
            self.get_workload_data(), ensure_ascii=False
        )

        # Dropdown punjenje
        context["lista_projekata"] = Projekt.objects.filter(is_active=True).order_by(
            "naziv_projekta"
        )
        context["lista_radnika"] = Employee.objects.filter(is_active=True).order_by(
            "last_name", "first_name"
        )

        # Include GrupaPoslova data
        context["grupe_poslova"] = self.get_grupa_poslova_data()

        context["odabrani_projekt_id"] = projekt_id
        context["odabrani_radnik_id"] = radnik_id

        return render(request, self.template_name, context)

    def get_director_context(self):
        """
        Slično kao get_vlasnik_direktor_context u prethodnim primjerima –
        ali nazovimo ga get_director_context.
        """
        projekti = Projekt.objects.filter(is_active=True)
        ukupni_projekti = projekti.count()
        zavrseni_projekti = projekti.filter(status="ZAVRSENO").count()
        ukupni_profit = (
            projekti.aggregate(total=Sum("financial_details__stvarni_profit"))["total"]
            or 0
        )
        ukupni_troskovi = (
            projekti.aggregate(total=Sum("financial_details__stvarni_troskovi"))[
                "total"
            ]
            or 0
        )

        radni_nalozi = RadniNalog.objects.filter(projekt__in=projekti, is_active=True)
        ukupni_nalozi = radni_nalozi.count()
        zavrseni_nalozi = radni_nalozi.filter(status="ZAVRSENO").count()
        progres = (
            int((zavrseni_nalozi / ukupni_nalozi) * 100) if ukupni_nalozi > 0 else 0
        )

        notifikacije_neprocitane = Notifikacija.objects.filter(
            korisnik=self.request.user, procitano=False
        ).count()
        notifikacije = Notifikacija.objects.filter(
            korisnik=self.request.user, procitano=False
        ).order_by("-created_at")[:5]

        aktivnosti = PovijestPromjena.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )[:10]

        ukupna_zarada = ukupni_profit - ukupni_troskovi

        return {
            "ukupni_projekti": ukupni_projekti,
            "zavrseni_projekti": zavrseni_projekti,
            "ukupni_profit": ukupni_profit,
            "ukupni_troskovi": ukupni_troskovi,
            "ukupni_nalozi": ukupni_nalozi,
            "zavrseni_nalozi": zavrseni_nalozi,
            "progres": progres,
            "notifikacije_neprocitane": notifikacije_neprocitane,
            "notifikacije": notifikacije,
            "aktivnosti": aktivnosti,
            "ukupna_zarada": ukupna_zarada,
            "radni_nalozi": radni_nalozi,
            "projekti": projekti,
        }

    def get_voditelj_context(self):
        # Slično “get_director_context” ali s manjim obuhvatom
        radni_nalozi = RadniNalog.objects.filter(is_active=True).select_related(
            "projekt", "grupa_posla"
        )
        ukupni_nalozi = radni_nalozi.count()
        zavrseni_nalozi = radni_nalozi.filter(status="ZAVRSENO").count()
        progres = (
            int((zavrseni_nalozi / ukupni_nalozi) * 100) if ukupni_nalozi > 0 else 0
        )

        notifikacije_neprocitane = Notifikacija.objects.filter(
            korisnik=self.request.user, procitano=False
        ).count()
        notifikacije = Notifikacija.objects.filter(
            korisnik=self.request.user, procitano=False
        ).order_by("-created_at")[:5]
        aktivnosti = PovijestPromjena.objects.filter(user=self.request.user).order_by(
            "-created_at"
        )[:10]

        return {
            "radni_nalozi": radni_nalozi,
            "ukupni_nalozi": ukupni_nalozi,
            "zavrseni_nalozi": zavrseni_nalozi,
            "progres": progres,
            "notifikacije_neprocitane": notifikacije_neprocitane,
            "notifikacije": notifikacije,
            "aktivnosti": aktivnosti,
        }

    def get_radnik_context(self, radnik):
        radni_nalozi = (
            RadniNalog.objects.filter(
                Q(zadužena_osoba=radnik) | Q(dodatne_osobe=radnik), is_active=True
            )
            .select_related("projekt", "grupa_posla")
            .distinct()
        )

        ukupni_nalozi = radni_nalozi.count()
        zavrseni_nalozi = radni_nalozi.filter(status="ZAVRSENO").count()
        progres = (
            int((zavrseni_nalozi / ukupni_nalozi) * 100) if ukupni_nalozi > 0 else 0
        )

        notifikacije_neprocitane = Notifikacija.objects.filter(
            korisnik=radnik.user, procitano=False
        ).count()
        notifikacije = Notifikacija.objects.filter(
            korisnik=radnik.user, procitano=False
        ).order_by("-created_at")[:5]
        aktivnosti = PovijestPromjena.objects.filter(user=radnik.user).order_by(
            "-created_at"
        )[:10]

        return {
            "radnik": radnik,
            "radni_nalozi": radni_nalozi,
            "ukupni_nalozi": ukupni_nalozi,
            "zavrseni_nalozi": zavrseni_nalozi,
            "progres": progres,
            "notifikacije_neprocitane": notifikacije_neprocitane,
            "notifikacije": notifikacije,
            "aktivnosti": aktivnosti,
            "ukupna_zarada": 0,
        }

    def get_financial_material_context(self):
        """Primjer: materijalno-financijski info."""
        total_materijal_cost = Decimal("0.00")
        all_materijali = Materijal.objects.filter(
            is_active=True
        )  # Removed select_related
        # If Materijal has a related field, replace 'some_related_field' with the actual field name:
        # all_materijali = Materijal.objects.filter(is_active=True).select_related('actual_related_field')
        for mat in all_materijali:
            total_materijal_cost += mat.cijena * mat.kolicina

        projekti = Projekt.objects.filter(is_active=True)
        probijen_budget_count = 0
        najveci_trosak = Decimal("0.00")
        projekt_s_najvecim_troskom = None

        for p in projekti:
            if p.stvarni_troskovi > (p.predvidjeni_troskovi or 0):
                probijen_budget_count += 1
            if p.stvarni_troskovi > najveci_trosak:
                najveci_trosak = p.stvarni_troskovi
                projekt_s_najvecim_troskom = p

        total_stvarni_troskovi = sum(
            p.stvarni_troskovi for p in projekti if p.stvarni_troskovi
        )

        return {
            "total_materijal_cost": total_materijal_cost,
            "probijen_budget_count": probijen_budget_count,
            "projekt_s_najvecim_troskom": projekt_s_najvecim_troskom,
            "najveci_trosak": najveci_trosak,
            "total_stvarni_troskovi": total_stvarni_troskovi,
        }

    def get_grupa_poslova_data(self):
        """Dohvati sve aktivne grupe poslova."""
        grupe_poslova = GrupaPoslova.objects.filter(is_active=True).order_by("naziv")
        return grupe_poslova

    def get_filtered_radni_nalozi(self, projekt_id=None, radnik_id=None):
        """Dohvati radne naloge filtrirane po projektu ili radniku."""
        qs = RadniNalog.objects.filter(is_active=True).select_related(
            "projekt", "grupa_posla"
        )
        if projekt_id:
            qs = qs.filter(projekt_id=projekt_id)
        if radnik_id:
            # radnik može biti zaduzena_osoba ili u dodatne_osobe (M2M)
            qs = qs.filter(
                Q(zaduzena_osoba_id=radnik_id) | Q(dodatne_osobe__id=radnik_id)
            ).distinct()  # Corrected field name
        return qs.order_by("naziv_naloga")

    def get_gantt_data(self, radni_nalozi):
        """
        Vrati listu dict-ova za dhtmlxGantt (ili custom tablični prikaz).
        """
        tasks = []
        for nalog in radni_nalozi:
            start_str = ""
            if nalog.datum_pocetka:
                start_str = nalog.datum_pocetka.strftime("%Y-%m-%d")
            if nalog.datum_zavrsetka:
                nalog.datum_zavrsetka.strftime("%Y-%m-%d")
            progress_val = float(nalog.postotak_napretka) / 100.0
            task_text = (
                f"[{nalog.projekt.naziv_projekta}] {nalog.naziv_naloga}"
                if nalog.projekt
                else nalog.naziv_naloga
            )

            # Ako nema end_date, izračunaj "trajanje" 1
            duration_val = 1
            if nalog.datum_pocetka and nalog.datum_zavrsetka:
                delta = (nalog.datum_zavrsetka - nalog.datum_pocetka).days
                duration_val = delta if delta > 0 else 1

            task = {
                "id": nalog.pk,
                "text": task_text,
                "start_date": start_str,
                "duration": duration_val,
                "progress": progress_val,
                "projekt": nalog.projekt.naziv_projekta if nalog.projekt else "",
            }
            tasks.append(task)
        return tasks

    def get_workload_data(self):
        """
        Vraća listu { 'radnik': 'ime prezime', 'hours': <ukupno sati> }
        za sve radnike (ili partial).
        """
        # Preuzet ćemo zbroj sati_rada iz Angazman.
        employees = Employee.objects.filter(is_active=True).select_related("position")
        data_list = []
        for emp in employees:
            total_hours = (
                Angazman.objects.filter(zaposlenik=emp, is_active=True).aggregate(
                    total=Sum("sati_rada")
                )["total"]
                or 0
            )
            data_list.append(
                {
                    "radnik": f"{emp.first_name} {emp.last_name}",
                    "hours": float(total_hours),
                }
            )
        return data_list


@login_required
def api_dashboard_data(request):
    """API za dohvaćanje podataka o dashboardu."""
    korisnik = request.user

    if korisnik.is_superuser:
        projekti = Projekt.objects.filter(is_active=True)
        radni_nalozi = RadniNalog.objects.filter(projekt__in=projekti, is_active=True)
        ukupni_nalozi = radni_nalozi.count()
        zavrseni_nalozi = radni_nalozi.filter(status="ZAVRSENO").count()
        progres = (
            int((zavrseni_nalozi / ukupni_nalozi) * 100) if ukupni_nalozi > 0 else 0
        )

        response_data = {
            "projekti": projekti.count(),
            "profit": projekti.aggregate(profit=Sum("stvarni_profit"))["profit"] or 0,
            "ukupni_nalozi": ukupni_nalozi,
            "zavrseni_nalozi": zavrseni_nalozi,
            "progres": progres,
            "zaposleni": Employee.objects.count(),
            "notifikacije_neprocitane": Notifikacija.objects.filter(
                korisnik=korisnik, procitano=False
            ).count(),
        }
    elif hasattr(korisnik, "employee"):
        employee = korisnik.employee
        position_title = employee.position.title

        if position_title in ["Direktor", "Voditelj"]:
            projekti = Projekt.objects.filter(is_active=True)
            radni_nalozi = RadniNalog.objects.filter(
                projekt__in=projekti, is_active=True
            )
            ukupni_nalozi = radni_nalozi.count()
            zavrseni_nalozi = radni_nalozi.filter(status="ZAVRSENO").count()
            progres = (
                int((zavrseni_nalozi / ukupni_nalozi) * 100) if ukupni_nalozi > 0 else 0
            )

            response_data = {
                "projekti": projekti.count(),
                "profit": projekti.aggregate(profit=Sum("stvarni_profit"))["profit"]
                or 0,
                "ukupni_nalozi": ukupni_nalozi,
                "zavrseni_nalozi": zavrseni_nalozi,
                "progres": progres,
                "zaposleni": Employee.objects.count(),
                "notifikacije_neprocitane": Notifikacija.objects.filter(
                    korisnik=korisnik, procitano=False
                ).count(),
            }
        else:
            # Radnik ili drugi
            radni_nalozi = RadniNalog.objects.filter(
                Q(zadužena_osoba=employee) | Q(dodatne_osobe=employee), is_active=True
            ).distinct()
            ukupni_nalozi = radni_nalozi.count()
            zavrseni_nalozi = radni_nalozi.filter(status="ZAVRSENO").count()
            progres = (
                int((zavrseni_nalozi / ukupni_nalozi) * 100) if ukupni_nalozi > 0 else 0
            )

            response_data = {
                "radni_nalozi": ukupni_nalozi,
                "zavrseni_nalozi": zavrseni_nalozi,
                "progres": progres,
                "notifikacije_neprocitane": Notifikacija.objects.filter(
                    korisnik=korisnik, procitano=False
                ).count(),
            }
    else:
        response_data = {}

    return JsonResponse(response_data)


class ProjektListView(ListView):
    model = Projekt
    template_name = "nalozi/lista_projekata.html"
    context_object_name = "projekti"
    paginate_by = 10

    def get_queryset(self):
        return Projekt.objects.filter(is_active=True).order_by("naziv_projekta")


@login_required
def dashboard_view(request):
    """Dashboard view for proizvodnja app"""
    if not hasattr(request.user, "employee"):
        messages.error(request, "Nemate pristup. Potreban je profil zaposlenika.")
        return redirect("login")

    # Get user's role/position
    employee = request.user.employee
    position = employee.position.title if employee.position else None

    context = get_dashboard_context(request.user, position)
    return render(request, "proizvodnja/dashboard.html", context)


def get_dashboard_context(user, position):
    """Get appropriate dashboard context based on user role"""
    context = {
        "projekti": Projekt.objects.filter(is_active=True)[:5],
        "radni_nalozi": RadniNalog.objects.filter(is_active=True)[:5],
        "recent_activities": PovijestPromjena.objects.all()[:10],
    }

    # Add role-specific data
    if position in ["Direktor", "Administrator"]:
        context.update(get_management_context())
    elif position in ["Voditelj Proizvodnje", "Voditelj Projekta"]:
        context.update(get_supervisor_context())
    else:
        context.update(get_worker_context(user.employee))

    return context


def get_management_context():
    """Get context data for management dashboard"""
    return {
        "total_projects": Projekt.objects.count(),
        "active_projects": Projekt.objects.filter(status="U_TIJEKU").count(),
        "financial_summary": calculate_project_costs(None),  # None for all projects
        "proizvodnja_stats": ProizvodnjaStatistika.objects.all(),
    }


def get_supervisor_context():
    """Get context data for supervisor dashboard"""
    return {
        "ongoing_work": RadniNalog.objects.filter(status="U_TIJEKU").count(),
        "pending_reviews": RadniNalog.objects.filter(status="CEKA_OCJENU").count(),
    }


def get_worker_context(employee):
    """Get context data for worker dashboard"""
    return {
        "my_tasks": RadniNalog.objects.filter(employee=employee, status="U_TIJEKU"),
        "completed_tasks": RadniNalog.objects.filter(
            employee=employee, status="ZAVRSENO"
        ),
    }
