from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View

from .models import Projekt, RadniNalog, Zaposlenik


@login_required
def home_view(request):
    """Prikazuje početnu stranicu s opcijama na temelju uloge korisnika."""
    context = {
        "user": request.user,
    }
    return render(request, "nalozi/home.html", context)


class DashboardView(LoginRequiredMixin, View):
    template_name = "dashboard.html"

    def get(self, request, *args, **kwargs):
        """
        Prikazuje dashboard na temelju uloge korisnika.
        """
        # Provjera korisničke role
        if request.user.is_staff or (
            hasattr(request.user, "zaposlenik")
            and request.user.zaposlenik.role in ["Administrator", "Voditelj Proizvodnje"]
        ):
            context = self.get_admin_context()
        elif hasattr(request.user, "zaposlenik"):
            context = self.get_radnik_context(request.user.zaposlenik)
        else:
            context = {}  # Ako korisnik nema odgovarajuću ulogu
        return render(request, self.template_name, context)

    def get_admin_context(self):
        """
        Kontekst za administratore i voditelje proizvodnje.
        """
        projekti = Projekt.objects.filter(is_active=True)
        radni_nalozi = RadniNalog.objects.filter(is_active=True)

        ukupni_nalozi = radni_nalozi.count()
        zavrseni_nalozi = radni_nalozi.filter(status="Završen").count()
        progres = int((zavrseni_nalozi / ukupni_nalozi) * 100) if ukupni_nalozi > 0 else 0

        return {
            "projekti": projekti,
            "ukupni_nalozi": ukupni_nalozi,
            "zavrseni_nalozi": zavrseni_nalozi,
            "progres": progres,
            "aktivnosti": [],  # Možete dodati logiku za aktivnosti
            "radni_nalozi": radni_nalozi,
        }

    def get_radnik_context(self, radnik):
        """
        Kontekst za radnike.
        """
        radni_nalozi = radnik.get_radni_nalozi()

        ukupni_nalozi = radni_nalozi.count()
        zavrseni_nalozi = radni_nalozi.filter(status="Završen").count()
        progres = int((zavrseni_nalozi / ukupni_nalozi) * 100) if ukupni_nalozi > 0 else 0

        return {
            "radnik": radnik,
            "ukupni_nalozi": ukupni_nalozi,
            "zavrseni_nalozi": zavrseni_nalozi,
            "progres": progres,
            "aktivnosti": radnik.get_neprocitane_notifikacije(),
            "radni_nalozi": radni_nalozi,
        }


@login_required
def api_dashboard_data(request):
    """
    API za dohvaćanje podataka o dashboardu.
    """
    korisnik = request.user
    if korisnik.is_staff or (
        hasattr(korisnik, "zaposlenik")
        and korisnik.zaposlenik.role in ["Administrator", "Voditelj Proizvodnje"]
    ):
        response_data = {
            "projekti": Projekt.objects.filter(is_active=True).count(),
            "radni_nalozi": RadniNalog.objects.filter(is_active=True).count(),
            "zaposleni": Zaposlenik.objects.filter(is_active=True).count(),
        }
    elif hasattr(korisnik, "zaposlenik"):
        radnik = korisnik.zaposlenik
        response_data = {
            "radni_nalozi": radnik.get_radni_nalozi().count(),
            "angazmani": radnik.get_aktivni_angazmani().count(),
            "ocjene": radnik.get_ocjene().count(),
            "ukupno_sati": radnik.get_ukupno_sati(),
            "trenutna_placa": radnik.izracunaj_zaradu(),
            "bonusi": radnik.izracunaj_ukupne_bonuse(),
        }
    else:
        response_data = {}

    return JsonResponse(response_data)
