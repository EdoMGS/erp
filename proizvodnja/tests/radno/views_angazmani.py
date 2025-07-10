from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import AngazmanForm, DodatniAngazmanForm
from .models import Angazman, RadniNalog
from .utils import log_action


# -------- 1. Lista angažmana -------- #
class ListaAngazmanaView(LoginRequiredMixin, ListView):
    model = Angazman
    template_name = "lista_angazmana.html"
    context_object_name = "angazmani"
    paginate_by = 10

    def get_queryset(self):
        """
        Dohvaća angažmane prema radnom nalogu ili zaposleniku.
        """
        radni_nalog_id = self.kwargs.get("radni_nalog_id")
        zaposlenik_id = self.kwargs.get("zaposlenik_id")

        if radni_nalog_id:
            queryset = (
                super()
                .get_queryset()
                .filter(radni_nalog_id=radni_nalog_id, is_active=True)
            )
        elif zaposlenik_id:
            queryset = (
                super()
                .get_queryset()
                .filter(zaposlenik_id=zaposlenik_id, is_active=True)
            )
        else:
            queryset = super().get_queryset().filter(is_active=True)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if "radni_nalog_id" in self.kwargs:
            context["radni_nalog"] = get_object_or_404(
                RadniNalog, id=self.kwargs["radni_nalog_id"]
            )
        return context


# -------- 2. Dodavanje angažmana -------- #
class DodajAngazmanView(LoginRequiredMixin, CreateView):
    model = Angazman
    form_class = AngazmanForm
    template_name = "dodaj_angazman.html"

    def form_valid(self, form):
        instance = form.save(commit=False)
        radni_nalog_id = self.kwargs.get("radni_nalog_id")
        if radni_nalog_id:
            instance.radni_nalog = get_object_or_404(RadniNalog, id=radni_nalog_id)
        instance.save()
        form.save_m2m()
        try:
            from .utils import log_action

            log_action(self.request.user, instance, "CREATE", form.cleaned_data)
        except ImportError:
            pass
        messages.success(self.request, "Angažman uspješno dodan!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy(
            "lista_angazmana", kwargs={"radni_nalog_id": self.kwargs["radni_nalog_id"]}
        )


# -------- 3. Ažuriranje angažmana -------- #
class AzurirajAngazmanView(LoginRequiredMixin, UpdateView):
    model = Angazman
    form_class = AngazmanForm
    template_name = "dodaj_angazman.html"

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.save()
        form.save_m2m()
        try:
            from .utils import log_action

            log_action(self.request.user, instance, "UPDATE", form.cleaned_data)
        except ImportError:
            pass
        messages.success(self.request, "Angažman uspješno ažuriran!")
        return super().form_valid(form)

        messages.success(self.request, "Angažman uspješno ažuriran!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy(
            "lista_angazmana", kwargs={"radni_nalog_id": self.object.radni_nalog.id}
        )


# -------- 4. Dodavanje dodatnog angažmana -------- #
class DodajDodatniAngazmanView(LoginRequiredMixin, CreateView):
    model = Angazman
    form_class = DodatniAngazmanForm
    template_name = "dodaj_dodatni_angazman.html"

    def dispatch(self, request, *args, **kwargs):
        """
        Provjera prava korisnika za dodavanje dodatnog angažmana.
        """
        if not request.user.is_staff and request.user.role != "Voditelj Proizvodnje":
            messages.error(request, "Nemate dozvolu za dodavanje dodatnog angažmana.")
            return redirect("home")
        return super().dispatch(request, *args, **kwargs)

        def form_valid(self, form):
            """
            Sprema dodatni angažman uz obavezno obrazloženje.
            """
            angazman = form.save(commit=False)
            angazman.radni_nalog = get_object_or_404(
                RadniNalog, id=self.kwargs["radni_nalog_id"]
            )
            angazman.je_dodatni = True
            angazman.odobreno = self.request.user.zaposlenik
            angazman.save()
            form.save_m2m()

            # Logiranje dodavanja
            log_action(
                self.request.user, angazman, "DODATNI_ANGAZMAN", form.cleaned_data
            )

            messages.success(self.request, "Dodatni angažman uspješno dodan.")
            return redirect("lista_angazmana", radni_nalog_id=angazman.radni_nalog.id)


# -------- 5. Brisanje angažmana -------- #
class ObrisiAngazmanView(LoginRequiredMixin, DeleteView):
    model = Angazman
    template_name = "obrisi_angazman.html"

    def delete(self, request, *args, **kwargs):
        """
        Implementira "soft delete" za angažmane.
        """
        angazman = self.get_object()
        angazman.is_active = False
        angazman.save()

        # Logiranje brisanja
        log_action(request.user, angazman, "DELETE")

        messages.success(request, "Angažman uspješno obrisan!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy(
            "lista_angazmana", kwargs={"radni_nalog_id": self.object.radni_nalog.id}
        )


class DetaljiAngazmanaView(LoginRequiredMixin, DetailView):
    model = Angazman
    template_name = "detalji_angazmana.html"
    context_object_name = "angazman"

    def get_context_data(self, **kwargs):
        """
        Dodaje dodatne podatke za prikaz detalja angažmana.
        """
        context = super().get_context_data(**kwargs)
        angazman = self.get_object()
        context["radni_nalog"] = angazman.radni_nalog
        return context
