from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import MaterijalForm
from .models import Materijal, Projekt, RadniNalog
from .utils import log_action


# ==============================
# 1️⃣ Lista materijala
# ==============================
class ListaMaterijalaView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Materijal
    template_name = "proizvodnja/lista_materijala.html"  # Changed from nalozi/
    context_object_name = "materijali"
    paginate_by = 10

    def test_func(self):
        return self.request.user.groups.filter(
            name__in=["vlasnik", "direktor", "voditelj"]
        ).exists()

    def get_queryset(self):
        queryset = Materijal.objects.select_related("radni_nalog").filter(
            is_active=True
        )
        radni_nalog_id = self.kwargs.get("radni_nalog_id")
        projekt_id = self.kwargs.get("projekt_id")

        if radni_nalog_id:
            queryset = queryset.filter(radni_nalog_id=radni_nalog_id)
        elif projekt_id:
            queryset = queryset.filter(
                radni_nalog__projekt_id=projekt_id
            )  # Changed line

        # Apply filters from GET parameters
        naziv = self.request.GET.get("naziv")
        if naziv:
            queryset = queryset.filter(naziv__icontains=naziv)

        status_materijala = self.request.GET.get("status_materijala")
        if status_materijala:
            queryset = queryset.filter(status=status_materijala)

        return queryset.order_by("-created_at")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        radni_nalog_id = self.kwargs.get("radni_nalog_id")
        projekt_id = self.kwargs.get("projekt_id")

        if radni_nalog_id:
            context["radni_nalog"] = get_object_or_404(RadniNalog, id=radni_nalog_id)
        elif projekt_id:
            context["projekt"] = get_object_or_404(Projekt, id=projekt_id)

        return context


# ==============================
# 2️⃣ Detalji materijala
# ==============================
class DetaljiMaterijalaView(LoginRequiredMixin, DetailView):
    model = Materijal
    template_name = "detalji_materijala.html"
    context_object_name = "materijal"


# ==============================
# 3️⃣ Dodavanje materijala
# ==============================
class DodajMaterijalView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Materijal
    form_class = MaterijalForm
    template_name = "dodaj_materijal.html"

    def test_func(self):
        return self.request.user.groups.filter(
            name__in=["vlasnik", "direktor", "voditelj"]
        ).exists()

    @transaction.atomic
    def form_valid(self, form):
        materijal = form.save(commit=False)
        radni_nalog_id = self.kwargs.get("radni_nalog_id")
        projekt_id = self.kwargs.get("projekt_id")

        if radni_nalog_id:
            materijal.radni_nalog = get_object_or_404(RadniNalog, id=radni_nalog_id)
        elif projekt_id:
            materijal.projekt = get_object_or_404(
                Projekt, id=projekt_id
            )  # Ensure 'projekt' field exists if used

        inventory_item = form.cleaned_data.get("inventory_item")
        if inventory_item:
            inventory_item.quantity -= materijal.kolicina
            inventory_item.save()

        materijal.save()
        log_action(self.request.user, materijal, "CREATE", form.cleaned_data)
        messages.success(self.request, "Materijal uspješno dodan!")

        return redirect(self.get_success_url())

    def get_success_url(self):
        radni_nalog_id = self.object.radni_nalog.id if self.object.radni_nalog else None
        projekt_id = self.object.projekt.id if self.object.projekt else None

        if radni_nalog_id:
            return reverse_lazy(
                "lista_materijala", kwargs={"radni_nalog_id": radni_nalog_id}
            )
        if projekt_id:
            return reverse_lazy("lista_materijala", kwargs={"projekt_id": projekt_id})
        return reverse_lazy("lista_materijala")


# ==============================
# 4️⃣ Ažuriranje materijala
# ==============================
class AzurirajMaterijalView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Materijal
    form_class = MaterijalForm
    template_name = "dodaj_materijal.html"

    def test_func(self):
        return self.request.user.groups.filter(
            name__in=["vlasnik", "direktor", "voditelj"]
        ).exists()

    @transaction.atomic
    def form_valid(self, form):
        materijal = form.save()
        log_action(self.request.user, materijal, "UPDATE", form.cleaned_data)
        messages.success(self.request, "Materijal uspješno ažuriran!")
        return super().form_valid(form)

    def get_success_url(self):
        radni_nalog_id = self.object.radni_nalog.id if self.object.radni_nalog else None
        projekt_id = self.object.projekt.id if self.object.projekt else None

        if radni_nalog_id:
            return reverse_lazy(
                "lista_materijala", kwargs={"radni_nalog_id": radni_nalog_id}
            )
        if projekt_id:
            return reverse_lazy("lista_materijala", kwargs={"projekt_id": projekt_id})
        return reverse_lazy("lista_materijala")


# ==============================
# 5️⃣ Brisanje materijala
# ==============================
class ObrisiMaterijalView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Materijal
    template_name = "obrisi_materijal.html"

    def test_func(self):
        return self.request.user.groups.filter(
            name__in=["vlasnik", "direktor", "voditelj"]
        ).exists()

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        materijal = self.get_object()
        materijal.is_active = False
        materijal.save()
        log_action(request.user, materijal, "DELETE")
        messages.success(request, "Materijal uspješno obrisan!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        radni_nalog_id = self.object.radni_nalog.id if self.object.radni_nalog else None
        projekt_id = self.object.projekt.id if self.object.projekt else None

        if radni_nalog_id:
            return reverse_lazy(
                "lista_materijala", kwargs={"radni_nalog_id": radni_nalog_id}
            )
        if projekt_id:
            return reverse_lazy("lista_materijala", kwargs={"projekt_id": projekt_id})
        return reverse_lazy("lista_materijala")


# ...existing code...
from django.shortcuts import get_object_or_404, render

from .models import Materijal, RadniNalog


def lista_materijala(request, radni_nalog_id=None):
    if radni_nalog_id:
        radni_nalog = get_object_or_404(RadniNalog, id=radni_nalog_id)
        materijali = Materijal.objects.filter(radni_nalog=radni_nalog)
    else:
        materijali = Materijal.objects.all()
        radni_nalog = None

    context = {
        "materijali": materijali,
        "radni_nalog_id": radni_nalog_id,
        "radni_nalog": radni_nalog,
    }
    return render(
        request, "proizvodnja/lista_materijala.html", context
    )  # Changed from nalozi/


# ...existing code...
