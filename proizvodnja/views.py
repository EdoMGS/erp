from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, UpdateView

from financije.services import (calculate_project_costs,
                                process_completed_work_order)
from ljudski_resursi.models import Employee
from projektiranje_app.models import CADDocument
from skladiste.models import Materijal

from .forms import (AngazmanForm, OcjenaKvaliteteForm, ProjektForm,
                    RadniNalogForm, RadniNalogMaterijalForm,
                    VideoMaterijalForm, VideoPitanjeForm)
from .models import Projekt, RadniNalog
from .views_dashboard import dashboard_view


@login_required
def proizvodnja_home(request):
    """Homepage view for proizvodnja app"""
    context = {
        "user": request.user,
        "has_access": request.user.is_superuser or hasattr(request.user, "employee_profile"),
    }
    return render(request, "proizvodnja/home.html", context)


@login_required
def centralni_panel(request):
    """Centralni panel view"""
    if not hasattr(request.user, "employee"):
        messages.error(request, "Nemate pristup. Potreban je profil zaposlenika.")
        return redirect("login")

    context = {
        "projekti": Projekt.objects.filter(is_active=True),
        "radni_nalozi": RadniNalog.objects.filter(is_active=True),
        "zaposlenici": Employee.objects.filter(is_active=True),
        "materijali": Materijal.objects.filter(is_active=True),
        "tehnicka_dokumentacija": CADDocument.objects.filter(is_active=True),
    }
    return render(request, "proizvodnja/centralni_panel.html", context)


@login_required
def projekt_add(request):
    """Dodavanje novog projekta."""
    if request.method == "POST":
        form = ProjektForm(request.POST)
        if form.is_valid():
            projekt = form.save()
            messages.success(request, "Projekt uspješno kreiran!")
            return redirect("proizvodnja:projekt_detail", pk=projekt.pk)
    else:
        form = ProjektForm()
    return render(
        request,
        "proizvodnja/dodaj_uredi_projekt.html",
        {"form": form, "action": "create", "title": "Dodaj Novi Projekt"},
    )


@login_required
def projekt_edit(request, pk):
    """Uređivanje postojećeg projekta."""
    projekt = get_object_or_404(Projekt, pk=pk)
    if request.method == "POST":
        form = ProjektForm(request.POST, instance=projekt)
        if form.is_valid():
            form.save()
            messages.success(request, "Projekt uspješno ažuriran!")
            return redirect("proizvodnja:projekt_detail", pk=projekt.pk)
    else:
        form = ProjektForm(instance=projekt)
    return render(
        request,
        "proizvodnja/dodaj_uredi_projekt.html",
        {"form": form, "action": "edit", "projekt": projekt, "title": "Uredi Projekt"},
    )


@login_required
def projekt_detail(request, pk):
    """Detaljni prikaz projekta."""
    projekt = get_object_or_404(Projekt, pk=pk)
    return render(request, "proizvodnja/projekt_detail.html", {"projekt": projekt})


@login_required
def lista_projekata(request):
    """View for listing all projects"""
    projekti = Projekt.objects.filter(is_active=True)

    # Handle search
    naziv = request.GET.get("naziv")
    if naziv:
        projekti = projekti.filter(naziv_projekta__icontains(naziv))

    # Handle status filter
    status = request.GET.get("status")
    if status:
        projekti = projekti.filter(status=status)

    return render(
        request,
        "proizvodnja/lista_projekata.html",
        {
            "projekti": projekti,
            "current_naziv": naziv,
            "current_status": status,
        },
    )


@login_required
def lista_radnih_naloga(request, projekt_id):
    """View for listing work orders for a specific project"""
    projekt = Projekt.objects.get(id=projekt_id)
    nalozi = RadniNalog.objects.filter(projekt=projekt, is_active=True)
    return render(
        request,
        "proizvodnja/lista_radnih_naloga.html",
        {"nalozi": nalozi, "projekt": projekt},
    )


@login_required
def lista_materijala(request):
    """View for listing materials"""
    materijali = Materijal.objects.filter(is_active=True)
    return render(request, "proizvodnja/lista_materijala.html", {"materijali": materijali})


@login_required
def lista_tehnicke_dokumentacije(request):
    """View for listing technical documentation"""
    dokumentacija = CADDocument.objects.filter(is_active=True)
    return render(
        request,
        "proizvodnja/lista_tehnicke_dokumentacije.html",
        {"dokumentacija": dokumentacija},
    )


class RadniNalogCompleteView(UpdateView):
    def form_valid(self, form):
        response = super().form_valid(form)
        if form.instance.status == "ZAVRSENO":
            # Koristi financijski servis umjesto direktnog računanja
            process_completed_work_order(form.instance)
        return response


@login_required
def radni_nalog_detail(request, pk):
    from .models import RadniNalog  # Ako već nije importirano

    radni_nalog = get_object_or_404(RadniNalog, pk=pk)
    return render(request, "proizvodnja/radni_nalog_detail.html", {"radni_nalog": radni_nalog})


@login_required
def radni_nalog_add(request):
    """View for adding a new work order."""
    from .forms import RadniNalogForm

    if request.method == "POST":
        form = RadniNalogForm(request.POST)
        if form.is_valid():
            radni_nalog = form.save()
            messages.success(request, "Radni nalog uspješno kreiran!")
            return redirect("proizvodnja:radni_nalog_detail", pk=radni_nalog.pk)
    else:
        form = RadniNalogForm()
    return render(request, "proizvodnja/radni_nalog_form.html", {"form": form, "action": "create"})


@login_required
def radni_nalog_edit(request, pk):
    """View for editing an existing work order."""
    from .forms import RadniNalogForm

    radni_nalog = get_object_or_404(RadniNalog, pk=pk)
    if request.method == "POST":
        form = RadniNalogForm(request.POST, instance=radni_nalog)
        if form.is_valid():
            form.save()
            messages.success(request, "Radni nalog uspješno ažuriran!")
            return redirect("proizvodnja:radni_nalog_detail", pk=radni_nalog.pk)
    else:
        form = RadniNalogForm(instance=radni_nalog)
    return render(
        request,
        "proizvodnja/radni_nalog_form.html",
        {"form": form, "action": "edit", "radni_nalog": radni_nalog},
    )


@login_required
def univerzalni_radni_nalog(request, pk=None, action="create"):
    """
    Universal view for work orders - handles creation, editing and viewing.
    """
    if pk:
        radni_nalog = get_object_or_404(RadniNalog, pk=pk)
    else:
        radni_nalog = None

    # Initialize all formsets
    MaterialFormSet = inlineformset_factory(RadniNalog, RadniNalogMaterijal, form=RadniNalogMaterijalForm, extra=1)
    VideoMaterijalFormSet = inlineformset_factory(RadniNalog, VideoMaterijal, form=VideoMaterijalForm, extra=1)
    VideoPitanjeFormSet = inlineformset_factory(RadniNalog, VideoPitanje, form=VideoPitanjeForm, extra=1)
    OcjenaKvaliteteFormSet = inlineformset_factory(RadniNalog, OcjenaKvalitete, form=OcjenaKvaliteteForm, extra=1)
    AngazmanFormSet = inlineformset_factory(RadniNalog, Angazman, form=AngazmanForm, extra=1)

    if request.method == "POST" and action != "view":
        form = RadniNalogForm(request.POST, instance=radni_nalog)
        # Initialize formsets with POST data
        materijal_formset = MaterialFormSet(request.POST, instance=radni_nalog)
        video_materijal_formset = VideoMaterijalFormSet(request.POST, request.FILES, instance=radni_nalog)
        video_pitanje_formset = VideoPitanjeFormSet(request.POST, instance=radni_nalog)
        ocjena_kvalitete_formset = OcjenaKvaliteteFormSet(request.POST, instance=radni_nalog)
        angazman_formset = AngazmanFormSet(request.POST, instance=radni_nalog)

        if (
            form.is_valid()
            and materijal_formset.is_valid()
            and video_materijal_formset.is_valid()
            and video_pitanje_formset.is_valid()
            and ocjena_kvalitete_formset.is_valid()
            and angazman_formset.is_valid()
        ):

            radni_nalog = form.save()
            materijal_formset.save()
            video_materijal_formset.save()
            video_pitanje_formset.save()
            ocjena_kvalitete_formset.save()
            angazman_formset.save()

            messages.success(request, "Radni nalog uspješno spremljen.")
            return redirect("proizvodnja:radni_nalog_detail", pk=radni_nalog.pk)
    else:
        form = RadniNalogForm(instance=radni_nalog)
        materijal_formset = MaterialFormSet(instance=radni_nalog)
        video_materijal_formset = VideoMaterijalFormSet(instance=radni_nalog)
        video_pitanje_formset = VideoPitanjeFormSet(instance=radni_nalog)
        ocjena_kvalitete_formset = OcjenaKvaliteteFormSet(instance=radni_nalog)
        angazman_formset = AngazmanFormSet(instance=radni_nalog)

    context = {
        "form": form,
        "action": action,
        "radni_nalog": radni_nalog,
        "materijal_formset": materijal_formset,
        "video_materijal_formset": video_materijal_formset,
        "video_pitanje_formset": video_pitanje_formset,
        "ocjena_kvalitete_formset": ocjena_kvalitete_formset,
        "angazman_formset": angazman_formset,
    }
    return render(request, "proizvodnja/univerzalni_radni_nalog.html", context)


class ProjektFinancialsView(DetailView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Koristi financijski servis
        context["financials"] = calculate_project_costs(self.object)
        return context


from django.contrib.auth.decorators import login_required


@login_required
def home(request):
    if request.user.is_authenticated:
        if request.user.is_superuser or hasattr(request.user, "employee_profile"):
            context = {
                "user": request.user,
                "projects": Projekt.objects.filter(is_active=True)[:5],
                "work_orders": RadniNalog.objects.filter(is_active=True)[:5],
            }
            return render(request, "proizvodnja/home.html", context)
        else:
            messages.warning(request, "Nemate potrebne dozvole za pristup.")
            return redirect("login")
    return redirect("login")


@login_required
def dashboard_view(request):
    context = {
        "user": request.user,
        "active_projects": Projekt.objects.filter(status="ACTIVE").count(),
        "completed_orders": RadniNalog.objects.filter(status="COMPLETED").count(),
        "recent_activities": RadniNalog.objects.all().order_by("-modified_at")[:5],
    }
    return render(request, "proizvodnja/dashboard.html", context)


@login_required
def centralni_panel_view(request):
    context = {
        "projekti": Projekt.objects.filter(is_active=True),
        "radni_nalozi": RadniNalog.objects.filter(is_active=True),
        "zaposlenici": Employee.objects.filter(is_active=True),
    }
    return render(request, "proizvodnja/centralni_panel.html", context)


@login_required
def proizvodnja_view(request):
    context = {
        "proizvodnja_stats": {
            "total_projects": Projekt.objects.count(),
            "active_orders": RadniNalog.objects.filter(status="ACTIVE").count(),
        }
    }
    return render(request, "proizvodnja/proizvodnja.html", context)
