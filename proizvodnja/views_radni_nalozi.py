# nalozi/views_radni_nalozi.py

import weasyprint
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, View

from ljudski_resursi.models import Employee  # Ako treba
# Import formi (prilagodi točno odakle ih povlačiš)
from proizvodnja.forms import OcjenaKvaliteteFormSet  # ako je tu
from proizvodnja.forms import \
    UstedaForm  # ako je to individual form, a ne inline formset
from proizvodnja.forms import (AngazmanFormSet, MaterijalFormSet,
                               RadniNalogForm, VideoMaterijalFormSet,
                               VideoPitanjeFormSet)
# Importi modela iz aplikacije "proizvodnja"
from proizvodnja.models import (GrupaPoslova, PovijestPromjena, Projekt,
                                RadniNalog, TemplateRadniNalog)

from .utils import log_action  # Ako imaš custom logging util

# Ako imaš i inline formset za Usteda, Nagrada, TehnickaDokumentacija itd.
# from proizvodnja.forms import NagradaFormSet, UstedaFormSet, TehnickaDokumentacijaFormSet

# Ako "TehnickaDokumentacijaFormSet" dolazi iz projektiranje_app.forms:
# from projektiranje_app.forms import TehnickaDokumentacijaFormSet

# Ako ti treba 'DesignTaskForm' ili slično:
# from projektiranje_app.forms import DesignTaskForm



# ------------------------------------------------------------
# Funkcije za obavijesti (websocket/email)
# ------------------------------------------------------------
def notify_via_websocket(korisnik, poruka):
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            f"notifikacije_{korisnik.id}",
            {"type": "send_notification", "message": poruka}
        )

def send_email_notification(subject, message, recipient_list):
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        fail_silently=False,
    )

# ------------------------------------------------------------
# 0) AJAX endpoint (ako treba dinamički dohvat grupe poslova)
# ------------------------------------------------------------
def ajax_load_grupe_poslova(request):
    tip_projekta_id = request.GET.get('tip_projekta_id')
    if tip_projekta_id:
        grupe = GrupaPoslova.objects.filter(tip_projekta_id=tip_projekta_id)
    else:
        grupe = GrupaPoslova.objects.none()
    data = [{'id': g.id, 'naziv': g.naziv} for g in grupe]
    return JsonResponse(data, safe=False)


# ------------------------------------------------------------
# 1) Lista Radnih Naloga
# ------------------------------------------------------------
class ListaRadnihNalogaView(LoginRequiredMixin, ListView):
    model = RadniNalog
    template_name = 'proizvodnja/lista_radnih_naloga.html'
    context_object_name = 'radni_nalozi'
    paginate_by = 20  # prilagodi
    
    def get_paginate_by(self, queryset):
        return self.request.GET.get('per_page', self.paginate_by)

    def get_queryset(self):
        projekt_id = self.kwargs.get('projekt_id')
        qs = (
            RadniNalog.objects.filter(projekt_id=projekt_id, is_active=True)
            .select_related('projekt', 'odgovorna_osoba', 'zaduzena_osoba')
            .prefetch_related('angazmani', 'materijali', 'video_materijali',
                              'video_pitanja', 'ocjene_kvalitete', 'nagrade', 'usteda')
            .order_by('-created_at')
        )

        naziv = self.request.GET.get('naziv', '').strip()
        if naziv:
            qs = qs.filter(naziv_naloga__icontains=naziv)

        status = self.request.GET.get('status', '')
        if status:
            qs = qs.filter(status=status)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        projekt_id = self.kwargs.get('projekt_id')
        projekt = get_object_or_404(Projekt, id=projekt_id)
        context['projekt'] = projekt

        context['prioriteti'] = RadniNalog.PRIORITETI_CHOICES
        context['tipovi_posla'] = RadniNalog.TIP_POSLA_CHOICES
        context['statusi_naloga'] = RadniNalog.STATUSI_NALOGA
        return context


# ------------------------------------------------------------
# 2) Detalji Radnog Naloga (Read-Only)
# ------------------------------------------------------------
class RadniNalogDetailView(LoginRequiredMixin, DetailView):
    model = RadniNalog
    template_name = 'proizvodnja/radni_nalog_detail.html'
    context_object_name = 'radni_nalog'

    def get_queryset(self):
        return (
            RadniNalog.objects.filter(is_active=True)
            .select_related('projekt', 'odgovorna_osoba', 'zaduzena_osoba')
            .prefetch_related('angazmani', 'materijali', 'video_materijali',
                              'video_pitanja', 'ocjene_kvalitete', 'nagrade', 'usteda')
        )


# ------------------------------------------------------------
# 3) Univerzalni Radni Nalog (kreiranje i uređivanje)
# ------------------------------------------------------------
class UniverzalniRadniNalogView(LoginRequiredMixin, UserPassesTestMixin, View):
    form_class = RadniNalogForm
    template_name = 'proizvodnja/univerzalni_radni_nalog.html'

    def test_func(self):
        """
        Tko smije kreirati ili uređivati radne naloge?
        Prilagodi prema grupama ili user.employee.logika
        """
        return self.request.user.groups.filter(name__in=['vlasnik','direktor','voditelj']).exists()

    def get(self, request, projekt_id, pk=None):
        projekt = get_object_or_404(Projekt, id=projekt_id)
        radni_nalog = get_object_or_404(RadniNalog, pk=pk) if pk else None

        form = self.form_class(instance=radni_nalog)
        
        # Primjeri formseta - prilagodi
        angazman_formset = AngazmanFormSet(instance=radni_nalog, prefix='angazmani')
        materijal_formset = MaterijalFormSet(instance=radni_nalog, prefix='materijali')
        # Ako imaš npr. TehnickaDokumentacijaFormSet:
        # dokumentacija_formset = TehnickaDokumentacijaFormSet(instance=radni_nalog, prefix='dokumentacije')
        video_materijal_formset = VideoMaterijalFormSet(instance=radni_nalog, prefix='video_materijali')
        video_pitanje_formset = VideoPitanjeFormSet(instance=radni_nalog, prefix='video_pitanja')
        ocjena_kvalitete_formset = OcjenaKvaliteteFormSet(instance=radni_nalog, prefix='ocjene_kvalitete')
        # Ako imaš NagradaFormSet i UstedaFormSet:
        # nagrada_formset = NagradaFormSet(instance=radni_nalog, prefix='nagrade')
        # usteda_formset = UstedaFormSet(instance=radni_nalog, prefix='ustede')

        content_type = ContentType.objects.get_for_model(RadniNalog)
        povijest_promjena = []
        if radni_nalog:
            povijest_promjena = PovijestPromjena.objects.filter(
                content_type=content_type,
                object_id=radni_nalog.id
            ).order_by('-created_at')

        context = {
            'projekt': projekt,
            'radni_nalog': radni_nalog,
            'form': form,
            'action': 'edit' if pk else 'create',
            'angazman_formset': angazman_formset,
            'materijal_formset': materijal_formset,
            # 'dokumentacija_formset': dokumentacija_formset,
            'video_materijal_formset': video_materijal_formset,
            'video_pitanje_formset': video_pitanje_formset,
            'ocjena_kvalitete_formset': ocjena_kvalitete_formset,
            # 'nagrada_formset': nagrada_formset,
            # 'usteda_formset': usteda_formset,
            'povijest_promjena': povijest_promjena,
        }
        return render(request, self.template_name, context)

    def post(self, request, projekt_id, pk=None):
        projekt = get_object_or_404(Projekt, id=projekt_id)
        radni_nalog = get_object_or_404(RadniNalog, pk=pk) if pk else None

        form = self.form_class(data=request.POST, files=request.FILES, instance=radni_nalog)
        
        angazman_formset = AngazmanFormSet(request.POST, request.FILES, instance=radni_nalog, prefix='angazmani')
        materijal_formset = MaterijalFormSet(request.POST, request.FILES, instance=radni_nalog, prefix='materijali')
        # dokumentacija_formset = TehnickaDokumentacijaFormSet(request.POST, request.FILES, instance=radni_nalog, prefix='dokumentacije')
        video_materijal_formset = VideoMaterijalFormSet(request.POST, request.FILES, instance=radni_nalog, prefix='video_materijali')
        video_pitanje_formset = VideoPitanjeFormSet(request.POST, request.FILES, instance=radni_nalog, prefix='video_pitanja')
        ocjena_kvalitete_formset = OcjenaKvaliteteFormSet(request.POST, request.FILES, instance=radni_nalog, prefix='ocjene_kvalitete')
        # nagrada_formset = NagradaFormSet(request.POST, request.FILES, instance=radni_nalog, prefix='nagrade')
        # usteda_formset = UstedaFormSet(request.POST, request.FILES, instance=radni_nalog, prefix='ustede')

        forms_valid = (
            form.is_valid()
            and angazman_formset.is_valid()
            and materijal_formset.is_valid()
            # and dokumentacija_formset.is_valid()
            and video_materijal_formset.is_valid()
            and video_pitanje_formset.is_valid()
            and ocjena_kvalitete_formset.is_valid()
            # and nagrada_formset.is_valid()
            # and usteda_formset.is_valid()
        )

        if forms_valid:
            try:
                with transaction.atomic():
                    nalog_obj = form.save(commit=False)
                    nalog_obj.projekt = projekt

                    if nalog_obj.status == 'U_TIJEKU':
                        if not nalog_obj.can_start():
                            messages.error(request, "Ne možete započeti ovaj nalog - preduvjeti nisu ispunjeni.")
                            return redirect('lista_radnih_naloga', projekt_id=projekt.id)

                    nalog_obj.save()
                    form.save_m2m()

                    # Spremi formsetove
                    angazman_formset.save()
                    materijal_formset.save()
                    # dokumentacija_formset.save()
                    video_materijal_formset.save()
                    video_pitanje_formset.save()
                    ocjena_kvalitete_formset.save()
                    # nagrada_formset.save()
                    # usteda_formset.save()

                    # Ako je ZAVRSENO -> postavi stvarno vrijeme = zbroj sati
                    if nalog_obj.status == 'ZAVRSENO':
                        total_sati = sum(ang.sati_rada for ang in nalog_obj.angazmani.all())
                        nalog_obj.stvarno_vrijeme = total_sati
                        nalog_obj.save(update_fields=['stvarno_vrijeme'])

                        # Ažuriraj template_nalog
                        if nalog_obj.template_nalog:
                            tmpl = nalog_obj.template_nalog
                            tmpl.broj_izvrsenja += 1
                            tmpl.akumulirani_sati += total_sati
                            tmpl.save()

                    # Bilježi promjenu
                    # log_action(...) ako koristiš custom
                    opis_promjene = {"status": "Ažurirano" if pk else "Kreirano"}
                    content_type = ContentType.objects.get_for_model(nalog_obj)
                    PovijestPromjena.objects.create(
                        content_type=content_type,
                        object_id=nalog_obj.id,
                        user=request.user,
                        promjene=opis_promjene
                    )

                    # Obavijesti menadžment
                    poruka = f"Radni nalog '{nalog_obj.naziv_naloga}' je {'ažuriran' if pk else 'kreiran'}."
                    korisnici_za_obavijesti = Employee.objects.filter(
                        position__title__in=['vlasnik','direktor','voditelj']
                    ).values_list('user', flat=True)
                    for usr_id in korisnici_za_obavijesti:
                        user_obj = get_object_or_404(User, id=usr_id)
                        notify_via_websocket(user_obj, poruka)
                        # send_email_notification("Obavijest o Radnom Nalogu", poruka, [user_obj.email])

                    messages.success(request, f"Radni nalog uspješno {'ažuriran' if pk else 'kreiran'}!")
                    return redirect('lista_radnih_naloga', projekt_id=projekt.id)

            except Exception as e:
                messages.error(request, f"Greška pri spremanju: {str(e)}")
        else:
            messages.error(request, "Greška pri validaciji forme.")

        context = {
            'projekt': projekt,
            'radni_nalog': radni_nalog,
            'form': form,
            'action': 'edit' if pk else 'create',
            'angazman_formset': angazman_formset,
            'materijal_formset': materijal_formset,
            # 'dokumentacija_formset': dokumentacija_formset,
            'video_materijal_formset': video_materijal_formset,
            'video_pitanje_formset': video_pitanje_formset,
            'ocjena_kvalitete_formset': ocjena_kvalitete_formset,
            # 'nagrada_formset': nagrada_formset,
            # 'usteda_formset': usteda_formset,
        }
        return render(request, self.template_name, context)


# ------------------------------------------------------------
# 4) Brisanje Radnog Naloga (soft-delete)
# ------------------------------------------------------------
class ObrisiRadniNalogView(LoginRequiredMixin, UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.groups.filter(name__in=['vlasnik','direktor','voditelj']).exists()

    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        nalog = get_object_or_404(RadniNalog, pk=pk)
        projekt = nalog.projekt
        nalog.is_active = False
        nalog.save()

        messages.success(request, "Radni nalog je uspješno obrisan (soft-delete).")
        if projekt:
            return redirect('lista_radnih_naloga', projekt_id=projekt.id)
        else:
            return redirect('dashboard')


# ------------------------------------------------------------
# 5) Ispis PDF-a Pojedinačnog Naloga
# ------------------------------------------------------------
class PrintPDFRadniNalogView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        nalog = get_object_or_404(RadniNalog, pk=pk, is_active=True)
        html_string = render_to_string('nalozi/pdf_radni_nalog.html', {
            'radni_nalog': nalog
        })
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="radni_nalog_{pk}.pdf"'

        weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
            response,
            stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + '/css/pdf_styles.css')]
        )
        return response


# ------------------------------------------------------------
# 6) Ispis PDF-a svih radnih naloga unutar projekta
# ------------------------------------------------------------
class PrintPDFSviNaloziView(LoginRequiredMixin, View):
    def get(self, request, projekt_id, *args, **kwargs):
        radni_nalozi = RadniNalog.objects.filter(projekt_id=projekt_id, is_active=True)
        projekt = get_object_or_404(Projekt, id=projekt_id)
        html_str = render_to_string('nalozi/pdf_svi_radni_naloga.html', {
            'radni_nalozi': radni_nalozi,
            'projekt': projekt
        })
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="radni_nalozi_projekt_{projekt_id}.pdf"'

        weasyprint.HTML(string=html_str, base_url=request.build_absolute_uri()).write_pdf(
            response,
            stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + '/css/pdf_styles.css')]
        )
        return response


# ------------------------------------------------------------
# 7) Generiranje PDF-a putem POST zahtjeva (alternativa)
# ------------------------------------------------------------
class GenerirajPDFRadniNalogView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        if not request.user.has_perm('proizvodnja.view_radninalog'):
            return HttpResponseForbidden("Nemate dopuštenje.")

        nalog = get_object_or_404(RadniNalog, pk=pk, is_active=True)
        html_string = render_to_string('nalozi/pdf_radni_nalog.html', {
            'radni_nalog': nalog
        })
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="radni_nalog_{pk}.pdf"'

        weasyprint.HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(
            response,
            stylesheets=[weasyprint.CSS(settings.STATIC_ROOT + '/css/pdf_styles.css')]
        )
        return response
