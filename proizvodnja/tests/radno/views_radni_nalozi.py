from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.mail import send_mail
from .models import RadniNalog, Projekt, Notifikacija, DodatniRadnik, Angazman, Zaposlenik
from .forms import RadniNalogForm, DodatniAngazmanForm
import math


# -------- 1. Lista radnih naloga -------- #
class ListaRadnihNalogaView(LoginRequiredMixin, ListView):
    model = RadniNalog
    template_name = 'lista_radnih_naloga.html'
    context_object_name = 'radni_nalozi'
    paginate_by = 10

    def get_queryset(self):
        projekt_id = self.kwargs['projekt_id']
        queryset = super().get_queryset().filter(projekt_id=projekt_id, is_active=True).order_by('-created_at')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projekt = get_object_or_404(Projekt, id=self.kwargs['projekt_id'])
        context['projekt'] = projekt
        return context


# -------- 2. Detalji radnog naloga -------- #
class DetaljiRadnogNalogaView(LoginRequiredMixin, DetailView):
    model = RadniNalog
    template_name = 'univerzalni_radni_nalozi.html'
    context_object_name = 'radni_nalog'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        radni_nalog = self.get_object()
        context['dodatni_radnici'] = radni_nalog.dodatni_radnici.all()
        context['usteda'] = self.izracunaj_ustede(radni_nalog)
        context['angazmani'] = Angazman.objects.filter(radni_nalog=radni_nalog)
        return context

    def izracunaj_ustede(self, radni_nalog):
        try:
            predviđeno = float(radni_nalog.predviđeno_vrijeme)
            stvarno = float(radni_nalog.stvarno_vrijeme)

            if predviđeno < 0 or stvarno < 0:
                raise ValueError("Vrijeme ne može biti negativno.")

            usteda = max(0, predviđeno - stvarno)
            return math.floor(usteda * 2) / 2
        except (TypeError, ValueError):
            return 0


# -------- 3. Kreiranje radnog naloga -------- #
class KreirajRadniNalogView(LoginRequiredMixin, CreateView):
    model = RadniNalog
    form_class = RadniNalogForm
    template_name = 'univerzalni_radni_nalozi.html'

    
        
            def form_valid(self, form):
                instance = form.save(commit=False)
                instance.save()  # Sprema instancu kako bi dobila ID
                form.save_m2m()  # Sada možemo raditi s ManyToMany poljima
                messages.success(self.request, "Uspješno ažurirano!")
                return super().form_valid(form)
            instance.save()  # Sprema instancu kako bi dobila ID
            form.save_m2m()  # Sada možemo raditi s ManyToMany poljima
            messages.success(self.request, "Uspješno ažurirano!")
            return super().form_valid(form)
        self.automatski_dodaj_angazmane(radni_nalog)
        messages.success(self.request, "Radni nalog i pripadajući angažmani uspješno kreirani!")
        return redirect('lista_radnih_naloga', projekt_id=radni_nalog.projekt.id)

    def automatski_dodaj_angazmane(self, radni_nalog):
        """
        Automatski dodaje angažmane za radni nalog na temelju tipa projekta.
        """
        radnici = Zaposlenik.objects.filter(role="Radnik", is_active=True)
        for radnik in radnici:
            Angazman.objects.create(
                radni_nalog=radni_nalog,
                zaposlenik=radnik,
                sati_rada=0  # Radnici će sami unositi stvarno vrijeme
            )


# -------- 4. Dodavanje dodatnog angažmana -------- #
class DodajDodatniAngazmanView(LoginRequiredMixin, CreateView):
    model = Angazman
    form_class = DodatniAngazmanForm
    template_name = 'dodaj_dodatni_angazman.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff and request.user.role != "Voditelj Proizvodnje":
            messages.error(request, "Nemate dozvolu za dodavanje dodatnog angažmana.")
            return redirect('home')
        return super().dispatch(request, *args, **kwargs)

    
        
            def form_valid(self, form):
                instance = form.save(commit=False)
                instance.save()  # Sprema instancu kako bi dobila ID
                form.save_m2m()  # Sada možemo raditi s ManyToMany poljima
                messages.success(self.request, "Uspješno ažurirano!")
                return super().form_valid(form)
            instance.save()  # Sprema instancu kako bi dobila ID
            form.save_m2m()  # Sada možemo raditi s ManyToMany poljima
            messages.success(self.request, "Uspješno ažurirano!")
            return super().form_valid(form)
        angazman.radni_nalog = get_object_or_404(RadniNalog, id=self.kwargs['radni_nalog_id'])
        angazman.je_dodatni = True
        angazman.odobreno = self.request.user.zaposlenik
        angazman.save()

        # Logiranje dodavanja
        log_action(self.request.user, angazman, "DODATNI_ANGAZMAN", form.cleaned_data)

        messages.success(self.request, "Dodatni angažman uspješno dodan.")
        return redirect('lista_angazmana', radni_nalog_id=angazman.radni_nalog.id)


# -------- 5. Ažuriranje radnog naloga -------- #
class AzurirajRadniNalogView(LoginRequiredMixin, UpdateView):
    model = RadniNalog
    form_class = RadniNalogForm
    template_name = 'univerzalni_radni_nalozi.html'

    
        
            def form_valid(self, form):
                instance = form.save(commit=False)
                instance.save()  # Sprema instancu kako bi dobila ID
                form.save_m2m()  # Sada možemo raditi s ManyToMany poljima
                messages.success(self.request, "Uspješno ažurirano!")
                return super().form_valid(form)
            instance.save()  # Sprema instancu kako bi dobila ID
            form.save_m2m()  # Sada možemo raditi s ManyToMany poljima
            messages.success(self.request, "Uspješno ažurirano!")
            return super().form_valid(form)
        radni_nalog.azuriraj_status()  # Pretpostavlja se da ova metoda postoji u modelu RadniNalog
        radni_nalog.save()

        # Provjera i obavijesti za bypass
        if radni_nalog.dokumentacija_bypass:
            poruka = f"Radni nalog '{radni_nalog.naziv_naloga}' koristi bypass tehničke dokumentacije."
            notify_via_websocket(radni_nalog.odgovorna_osoba.korisnik, poruka)

        if radni_nalog.bypass_materijala:
            poruka = f"Radni nalog '{radni_nalog.naziv_naloga}' koristi bypass materijala."
            notify_via_websocket(radni_nalog.odgovorna_osoba.korisnik, poruka)

        messages.success(self.request, "Radni nalog uspješno ažuriran!")
        return redirect('lista_radnih_naloga', projekt_id=radni_nalog.projekt.id)


# -------- 6. Brisanje radnog naloga -------- #
class ObrisiRadniNalogView(LoginRequiredMixin, DeleteView):
    model = RadniNalog
    template_name = 'obrisi_radni_nalog.html'

    def get_success_url(self):
        return reverse_lazy('lista_radnih_naloga', kwargs={'projekt_id': self.object.projekt.id})

    def delete(self, request, *args, **kwargs):
        radni_nalog = self.get_object()
        radni_nalog.is_active = False  # Umjesto fizičkog brisanja, postavlja is_active na False
        radni_nalog.save()

        # Logiranje brisanja
        log_action(request.user, radni_nalog, "OBRISAN_RADNI_NALOG")

        messages.success(request, "Radni nalog uspješno obrisan.")
        return redirect(self.get_success_url())


# -------- 7. Funkcije za slanje obavijesti -------- #
def notify_via_websocket(korisnik, poruka):
    channel_layer = get_channel_layer()
    group_name = f"notifikacije_{korisnik.id}"
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            "type": "send_notification",
            "message": poruka,
        }
    )


def notify_via_email(korisnik, poruka):
    if korisnik.email:
        send_mail(
            subject="Obavijest: Radni nalog",
            message=poruka,
            from_email="admin@mojaaplikacija.com",
            recipient_list=[korisnik.email],
        )
