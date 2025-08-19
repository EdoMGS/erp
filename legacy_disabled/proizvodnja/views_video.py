# nalozi/views_video.py

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import VideoMaterijalForm, VideoPitanjeForm
from .models import OcjenaKvalitete, RadniNalog, VideoMaterijal, VideoPitanje
from .utils import informiraj_korisnika  # Dodana funkcija ako je potrebna
from .utils import log_action


# ==============================
# 1️⃣ Video materijali
# ==============================
class ListaVideoMaterijalaView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = VideoMaterijal
    template_name = "tehnicke_dokumentacije/lista_tehnicke_dokumentacije.html"  # Provjerite putanju
    context_object_name = "video_materijali"
    paginate_by = 10

    def test_func(self):
        # Pristup imaju vlasnik, direktor i voditelj
        return self.request.user.groups.filter(name__in=["vlasnik", "direktor", "voditelj"]).exists()

    def get_queryset(self):
        projekt_id = self.kwargs.get("projekt_id")
        queryset = VideoMaterijal.objects.select_related("projekt").filter(is_active=True)
        if projekt_id:
            queryset = queryset.filter(projekt_id=projekt_id)
        return queryset.order_by("-created_at")


class DodajVideoMaterijalView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = VideoMaterijal
    form_class = VideoMaterijalForm
    template_name = "video_materijali/dodaj_video_materijal.html"

    def test_func(self):
        # Pristup imaju vlasnik, direktor i voditelj
        return self.request.user.groups.filter(name__in=["vlasnik", "direktor", "voditelj"]).exists()

    @transaction.atomic
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            video_materijal = self.object

            # Logiranje akcije
            log_action(self.request.user, video_materijal, "CREATE", form.cleaned_data)

            # Informiranje korisnika ako je potrebno
            informiraj_korisnika(video_materijal)  # Provjerite implementaciju ove funkcije

            messages.success(self.request, "Video materijal uspješno dodan!")
            return response
        except Exception as e:
            messages.error(self.request, f"Greška prilikom dodavanja video materijala: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Greška prilikom dodavanja video materijala.")
        return super().form_invalid(form)

    def get_success_url(self):
        projekt_id = self.object.projekt.id if self.object.projekt else None
        if projekt_id:
            return reverse_lazy("lista_video_materijala", kwargs={"projekt_id": projekt_id})
        return reverse_lazy("lista_video_materijala")


class AzurirajVideoMaterijalView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = VideoMaterijal
    form_class = VideoMaterijalForm
    template_name = "video_materijali/azuriraj_video_materijal.html"
    success_url = reverse_lazy("lista_video_materijala")

    def test_func(self):
        # Pristup imaju korisnik koji je dodao ili korisnici u grupi 'direktor'
        video_materijal = self.get_object()
        return self.request.user == video_materijal.dodao or self.request.user.groups.filter(name="direktor").exists()

    @transaction.atomic
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            video_materijal = self.object

            # Logiranje akcije
            log_action(self.request.user, video_materijal, "UPDATE", form.cleaned_data)

            # Informiranje korisnika ako je potrebno
            informiraj_korisnika(video_materijal)

            messages.success(self.request, "Video materijal uspješno ažuriran!")
            return response
        except Exception as e:
            messages.error(self.request, f"Greška prilikom ažuriranja video materijala: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Greška prilikom ažuriranja video materijala.")
        return super().form_invalid(form)


class ObrisiVideoMaterijalView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = VideoMaterijal
    template_name = "video_materijali/obrisi_video_materijal.html"

    def test_func(self):
        # Pristup imaju korisnik koji je dodao ili korisnici u grupi 'direktor'
        return self.request.user == self.get_object().dodao or self.request.user.groups.filter(name="direktor").exists()

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            video_materijal = self.get_object()
            video_materijal.is_active = False  # Soft delete
            video_materijal.save()

            # Logiranje akcije
            log_action(request.user, video_materijal, "DELETE")

            messages.success(request, "Video materijal uspješno obrisan!")
            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(request, f"Greška prilikom brisanja video materijala: {str(e)}")
            return redirect("lista_video_materijala")

    def get_success_url(self):
        projekt_id = self.object.projekt.id if self.object.projekt else None
        if projekt_id:
            return reverse_lazy("lista_video_materijala", kwargs={"projekt_id": projekt_id})
        return reverse_lazy("lista_video_materijala")


# ==============================
# 2️⃣ Video pitanja
# ==============================
class ListaVideoPitanjaView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = VideoPitanje
    template_name = "video_pitanja/lista_video_pitanja.html"
    context_object_name = "video_pitanja"
    paginate_by = 10

    def test_func(self):
        return self.request.user.groups.filter(name__in=["vlasnik", "direktor", "voditelj"]).exists()

    def get_queryset(self):
        radni_nalog_id = self.kwargs.get("radni_nalog_id", None)
        queryset = VideoPitanje.objects.filter(is_active=True)
        if radni_nalog_id:
            queryset = queryset.filter(radni_nalog_id=radni_nalog_id)
        return queryset.order_by("-created_at")


class DodajVideoPitanjeView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = VideoPitanje
    form_class = VideoPitanjeForm
    template_name = "video_pitanja/dodaj_video_pitanje.html"

    def test_func(self):
        # Pristup imaju vlasnik, direktor i voditelj
        return self.request.user.groups.filter(name__in=["vlasnik", "direktor", "voditelj"]).exists()

    @transaction.atomic
    def form_valid(self, form):
        try:
            video_pitanje = form.save(commit=False)
            radni_nalog_id = self.kwargs.get("radni_nalog_id", None)
            if radni_nalog_id:
                video_pitanje.radni_nalog = get_object_or_404(RadniNalog, id=radni_nalog_id)
            video_pitanje.dodao = self.request.user
            video_pitanje.save()

            # Logiranje akcije
            log_action(self.request.user, video_pitanje, "CREATE")

            messages.success(self.request, "Video pitanje uspješno dodano!")
            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(self.request, f"Greška prilikom dodavanja video pitanja: {str(e)}")
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Greška prilikom dodavanja video pitanja.")
        return super().form_invalid(form)

    def get_success_url(self):
        radni_nalog_id = self.kwargs.get("radni_nalog_id", None)
        if radni_nalog_id:
            return reverse_lazy("lista_video_pitanja", kwargs={"radni_nalog_id": radni_nalog_id})
        return reverse_lazy("lista_video_pitanja_bez_id")


class ObrisiVideoPitanjeView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = VideoPitanje
    template_name = "video_pitanja/obrisi_video_pitanje.html"

    def test_func(self):
        # Pristup imaju korisnik koji je dodao ili korisnici u grupi 'direktor'
        return self.request.user == self.get_object().dodao or self.request.user.groups.filter(name="direktor").exists()

    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        try:
            video_pitanje = self.get_object()
            video_pitanje.is_active = False  # Soft delete
            video_pitanje.save()

            # Logiranje akcije
            log_action(request.user, video_pitanje, "DELETE")

            messages.success(request, "Video pitanje uspješno obrisano!")
            return redirect(self.get_success_url())
        except Exception as e:
            messages.error(request, f"Greška prilikom brisanja video pitanja: {str(e)}")
            return redirect("lista_video_pitanja_bez_id")

    def get_success_url(self):
        radni_nalog_id = self.object.radni_nalog.id if self.object.radni_nalog else None
        if radni_nalog_id:
            return reverse_lazy("lista_video_pitanja", kwargs={"radni_nalog_id": radni_nalog_id})
        return reverse_lazy("lista_video_pitanja_bez_id")


# ==============================
# 3️⃣ Pregled medija u ocjenama
# ==============================
class PregledMedijaOcjeneView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = OcjenaKvalitete
    template_name = "video_ocjene/pregled_medija_ocjene.html"
    context_object_name = "ocjena"

    def test_func(self):
        # Pristup imaju direktor, voditelj, administrativno osoblje ili korisnik koji je dodao ocjenu
        ocjena = self.get_object()
        return (
            self.request.user.groups.filter(name__in=["direktor", "voditelj", "administrativno osoblje"]).exists()
            or self.request.user == ocjena.ocjenjivac.user
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ocjena = self.get_object()
        context["slike"] = ocjena.slike.all()  # Pretpostavka da je 'slike' ManyToManyField ili reverse FK
        context["video"] = ocjena.video  # Pretpostavka da je 'video' FK ili FileField
        return context
