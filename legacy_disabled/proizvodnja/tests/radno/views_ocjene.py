from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Avg
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import OcjenaKvaliteteForm
from .models import OcjenaKvalitete, RadniNalog
from .utils import log_action


# -------- 1. Lista ocjena kvalitete -------- #
class ListaOcjenaView(LoginRequiredMixin, ListView):
    model = OcjenaKvalitete
    template_name = "ocjene_kvalitete/lista_ocjena_kvalitete.html"
    context_object_name = "ocjene_kvalitete"
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().filter(is_active=True).order_by("-created_at")
        start_date = self.request.GET.get("start_date")
        end_date = self.request.GET.get("end_date")

        if start_date and end_date:
            queryset = queryset.filter(created_at__range=[start_date, end_date])

        if not self.request.user.is_superuser and self.request.user.role != "Direktor":
            queryset = queryset.filter(ocjenjivac=self.request.user)

        return queryset


# -------- 2. Detalji ocjene kvalitete -------- #
class DetaljiOcjeneKvaliteteView(LoginRequiredMixin, DetailView):
    model = RadniNalog
    template_name = "ocjene_kvalitete/detalji_ocjena_kvalitete.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        radni_nalog = self.get_object()

        # Grupiraj ocjene po razini
        context["ocjene_po_razinama"] = {
            "Voditelj": radni_nalog.ocjene_kvalitete.filter(razina="Voditelj"),
            "Direktor": radni_nalog.ocjene_kvalitete.filter(razina="Direktor"),
            "Neovisan": radni_nalog.ocjene_kvalitete.filter(razina="Neovisan"),
        }
        context["prosjek_ocjena"] = radni_nalog.ocjene_kvalitete.aggregate(avg=Avg("ocjena"))["avg"]
        return context


# -------- 3. Dodavanje ocjena -------- #
class DodajOcjenuView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = OcjenaKvalitete
    form_class = OcjenaKvaliteteForm
    template_name = "ocjene_kvalitete/dodaj_ocjenu_kvalitete.html"

    def test_func(self):
        return self.request.user.role in [
            "Voditelj",
            "Direktor",
            "Administrativno osoblje",
        ]

    def form_valid(self, form):
        instance = form.save(commit=False)
        # Ako postoji povezani zaposlenik, postavi ga kao ocjenjivača
        if hasattr(self.request.user, "zaposlenik"):
            instance.ocjenjivac = self.request.user.zaposlenik
        instance.save()
        form.save_m2m()
        # Validacija: Jedan ocjenjivač može ocijeniti samo jednom po razini.
        postoji_ocjena = OcjenaKvalitete.objects.filter(
            radni_nalog=instance.radni_nalog,
            ocjenjivac=instance.ocjenjivac,
            razina=instance.razina,
            is_active=True,
        ).exists()
        if postoji_ocjena:
            form.add_error("razina", "Već ste ocijenili ovaj radni nalog za svoju razinu.")
            return self.form_invalid(form)
        instance.save()
        messages.success(self.request, "Ocjena kvalitete uspješno dodana!")
        try:
            from .utils import informiraj_ocjenjivace, log_action

            informiraj_ocjenjivace(instance.radni_nalog)
            log_action(self.request.user, instance, "CREATE")
        except ImportError:
            pass
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("lista_ocjena_kvalitete")


# -------- 4. Ažuriranje ocjena -------- #
class AzurirajOcjenuView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = OcjenaKvalitete
    form_class = OcjenaKvaliteteForm
    template_name = "ocjene_kvalitete/dodaj_ocjenu_kvalitete.html"

    def test_func(self):
        ocjena = self.get_object()
        return self.request.user == ocjena.ocjenjivac or self.request.user.role == "Direktor"

        def form_valid(self, form):
            instance = form.save(commit=False)
            instance.save()  # Sprema instancu kako bi dobila ID
            form.save_m2m()  # Sada možemo raditi s ManyToMany poljima
            messages.success(self.request, "Ocjena kvalitete uspješno ažurirana!")
            log_action(self.request.user, instance, "UPDATE")
            return super().form_valid(form)


# -------- 5. Brisanje ocjena -------- #
class ObrisiOcjenuView(LoginRequiredMixin, DeleteView):
    model = OcjenaKvalitete
    template_name = "ocjene_kvalitete/obrisi_ocjenu_kvalitete.html"

    def delete(self, request, *args, **kwargs):
        ocjena = self.get_object()
        ocjena.is_active = False
        ocjena.save()
        messages.success(request, "Ocjena kvalitete uspješno obrisana!")
        log_action(request.user, ocjena, "DELETE")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("lista_ocjena_kvalitete")
