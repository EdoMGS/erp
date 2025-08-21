from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import VideoMaterijalForm, VideoPitanjeForm
from .models import OcjenaKvalitete, Projekt, RadniNalog, VideoMaterijal, VideoPitanje
from .utils import log_action


# -------- 1. Video materijali -------- #
class ListaVideoMaterijalaView(LoginRequiredMixin, ListView):
    model = VideoMaterijal
    template_name = "video_materijali/lista_video_materijala.html"
    context_object_name = "video_materijali"
    paginate_by = 10

    def get_queryset(self):
        """
        Dohvaća video materijale za određeni projekt.
        """
        projekt_id = self.kwargs.get("projekt_id")
        return VideoMaterijal.objects.filter(projekt_id=projekt_id, is_active=True).order_by(
            "-created_at"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projekt"] = get_object_or_404(Projekt, id=self.kwargs.get("projekt_id"))
        # Sakrij autora za radnike
        if (
            hasattr(self.request.user, "zaposlenik")
            and self.request.user.zaposlenik.access_level == "Radnik"
        ):
            for video in context["video_materijali"]:
                video.dodao = None
        return context


class DodajVideoMaterijalView(LoginRequiredMixin, CreateView):
    model = VideoMaterijal
    form_class = VideoMaterijalForm
    template_name = "video_materijali/dodaj_video_materijal.html"

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.save()  # Sprema instancu kako bi dobila ID
        form.save_m2m()  # Sada možemo raditi s ManyToMany poljima
        messages.success(self.request, "Uspješno ažurirano!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "lista_video_materijala", kwargs={"projekt_id": self.kwargs["projekt_id"]}
        )


class AzurirajVideoMaterijalView(LoginRequiredMixin, UpdateView):
    model = VideoMaterijal
    form_class = VideoMaterijalForm
    template_name = "video_materijali/azuriraj_video_materijal.html"

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.save()
        form.save_m2m()
        try:
            from .utils import log_action

            log_action(self.request.user, instance, "UPDATE")
        except ImportError:
            pass
        messages.success(self.request, "Video materijal uspješno ažuriran!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("lista_video_materijala", kwargs={"projekt_id": self.object.projekt.id})


class ObrisiVideoMaterijalView(LoginRequiredMixin, DeleteView):
    model = VideoMaterijal
    template_name = "video_materijali/obrisi_video_materijal.html"

    def delete(self, request, *args, **kwargs):
        video_materijal = self.get_object()
        video_materijal.is_active = False
        video_materijal.save()
        log_action(request.user, video_materijal, "DELETE")
        messages.success(request, "Video materijal uspješno obrisan!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy("lista_video_materijala", kwargs={"projekt_id": self.object.projekt.id})


# -------- 2. Video pitanja -------- #
class ListaVideoPitanjaView(LoginRequiredMixin, ListView):
    model = VideoPitanje
    template_name = "video_pitanja/lista_video_pitanja.html"
    context_object_name = "video_pitanja"
    paginate_by = 10

    def get_queryset(self):
        """
        Dohvaća video pitanja za određeni radni nalog.
        """
        radni_nalog_id = self.kwargs.get("radni_nalog_id")
        return VideoPitanje.objects.filter(radni_nalog_id=radni_nalog_id, is_active=True).order_by(
            "-created_at"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["radni_nalog"] = get_object_or_404(RadniNalog, id=self.kwargs.get("radni_nalog_id"))
        # Sakrij autora za radnike
        if (
            hasattr(self.request.user, "zaposlenik")
            and self.request.user.zaposlenik.access_level == "Radnik"
        ):
            for pitanje in context["video_pitanja"]:
                pitanje.dodao = None
        return context


class DodajVideoPitanjeView(LoginRequiredMixin, CreateView):
    model = VideoPitanje
    form_class = VideoPitanjeForm
    template_name = "video_pitanja/dodaj_video_pitanje.html"

    def form_valid(self, form):
        instance = form.save(commit=False)
        instance.radni_nalog = get_object_or_404(RadniNalog, id=self.kwargs.get("radni_nalog_id"))
        instance.save()  # Sprema instancu kako bi dobila ID
        form.save_m2m()  # Sada možemo raditi s ManyToMany poljima
        log_action(self.request.user, instance, "CREATE")
        messages.success(self.request, "Video pitanje uspješno dodano!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy(
            "lista_video_pitanja",
            kwargs={"radni_nalog_id": self.kwargs["radni_nalog_id"]},
        )


class ObrisiVideoPitanjeView(LoginRequiredMixin, DeleteView):
    model = VideoPitanje
    template_name = "video_pitanja/obrisi_video_pitanje.html"

    def delete(self, request, *args, **kwargs):
        video_pitanje = self.get_object()
        video_pitanje.is_active = False
        video_pitanje.save()
        log_action(request.user, video_pitanje, "DELETE")
        messages.success(request, "Video pitanje uspješno obrisano!")
        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy(
            "lista_video_pitanja", kwargs={"radni_nalog_id": self.object.radni_nalog.id}
        )


# -------- 3. Pregled medija u ocjenama -------- #
class PregledMedijaOcjeneView(LoginRequiredMixin, DetailView):
    model = OcjenaKvalitete
    template_name = "video_ocjene/pregled_medija_ocjene.html"
    context_object_name = "ocjena"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        ocjena = self.get_object()
        context["slike"] = ocjena.slike
        context["video"] = ocjena.video
        return context
