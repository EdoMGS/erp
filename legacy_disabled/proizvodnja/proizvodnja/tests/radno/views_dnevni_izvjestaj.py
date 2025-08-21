from datetime import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.template.loader import get_template
from django.views.generic import TemplateView, View
from xhtml2pdf import pisa

from .models import Angazman, OcjenaKvalitete, Projekt, RadniNalog


class DnevniIzvjestajView(LoginRequiredMixin, TemplateView):
    template_name = "dnevni_izvjestaj.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        datum = self.request.GET.get("datum", datetime.now().date())
        try:
            datum = datetime.strptime(datum, "%Y-%m-%d").date()
        except ValueError:
            datum = datetime.now().date()

        # Dohvaćanje statistika
        context["zavrseni_projekti"] = Projekt.objects.filter(
            status="Završeno", updated_at__date=datum
        ).count()
        context["zavrseni_radni_nalozi"] = RadniNalog.objects.filter(
            postotak_napretka=100, updated_at__date=datum
        ).count()
        context["aktivni_angazmani"] = Angazman.objects.filter(
            is_active=True, updated_at__date=datum
        ).count()
        context["ocjene_kvalitete"] = OcjenaKvalitete.objects.filter(created_at__date=datum).count()

        # Dohvaćanje detalja aktivnosti
        aktivnosti = list(
            Projekt.objects.filter(updated_at__date=datum).values(
                "id", "naziv_projekta", "updated_at"
            )
        )
        aktivnosti += list(
            RadniNalog.objects.filter(updated_at__date=datum).values(
                "id", "naziv_naloga", "updated_at"
            )
        )
        aktivnosti = sorted(aktivnosti, key=lambda x: x["updated_at"], reverse=True)

        # Prikaz podataka za aktivnosti
        context["aktivnosti"] = [
            {
                "tip": "Projekt" if "naziv_projekta" in a else "Radni Nalog",
                "opis": a.get("naziv_projekta") or a.get("naziv_naloga"),
                "created_at": a["updated_at"],
                "id": a["id"],
            }
            for a in aktivnosti
        ]

        return context


class GenerirajPDFDnevniIzvjestajView(LoginRequiredMixin, View):
    template_name = "dnevni_izvjestaj_pdf.html"

    def get(self, request, *args, **kwargs):
        datum = request.GET.get("datum", datetime.now().date())
        try:
            datum = datetime.strptime(datum, "%Y-%m-%d").date()
        except ValueError:
            datum = datetime.now().date()

        # Podaci za PDF
        context = {
            "datum": datum,
            "zavrseni_projekti": Projekt.objects.filter(
                status="Završeno", updated_at__date=datum
            ).count(),
            "zavrseni_radni_nalozi": RadniNalog.objects.filter(
                postotak_napretka=100, updated_at__date=datum
            ).count(),
            "aktivni_angazmani": Angazman.objects.filter(
                is_active=True, updated_at__date=datum
            ).count(),
            "ocjene_kvalitete": OcjenaKvalitete.objects.filter(created_at__date=datum).count(),
        }

        # Generiranje PDF-a
        template = get_template(self.template_name)
        html = template.render(context)
        response = HttpResponse(content_type="application/pdf")
        pisa_status = pisa.CreatePDF(html, dest=response)

        if pisa_status.err:
            return HttpResponse("Greška u generiranju PDF-a", status=500)

        return response
