# proizvodnja/views_api.py

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from ljudski_resursi.models import Nagrada  # Uvezite ako je potreban
from projektiranje_app.models import CADDocument
from projektiranje_app.serializers import CADDocumentSerializer

from .models import OcjenaKvalitete, RadniNalog
from .serializers import OcjenaKvaliteteSerializer, RadniNalogSerializer
from .utils import log_action


# ==============================
# 1️⃣ API za radne naloge
# ==============================
class ListaRadnihNalogaAPIView(generics.ListCreateAPIView):
    queryset = (
        RadniNalog.objects.all()
    )  # Možete dodati filter(is_active=True) po potrebi
    serializer_class = RadniNalogSerializer
    permission_classes = [IsAuthenticated]


class DetaljiRadnogNalogaAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        RadniNalog.objects.all()
    )  # Možete dodati filter(is_active=True) po potrebi
    serializer_class = RadniNalogSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        radni_nalog = serializer.save()
        log_action(self.request.user, radni_nalog, "UPDATE")

        # Slanje notifikacije putem Channels
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifikacije_{radni_nalog.odgovorna_osoba.user.id}",
            {
                "type": "send_notification",
                "message": f"Radni nalog '{radni_nalog.naziv_naloga}' je ažuriran.",
            },
        )


class KreirajRadniNalogAPIView(generics.CreateAPIView):
    queryset = RadniNalog.objects.all()
    serializer_class = RadniNalogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        radni_nalog = serializer.save()
        log_action(self.request.user, radni_nalog, "CREATE")

        # Slanje notifikacije putem Channels
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifikacije_{radni_nalog.odgovorna_osoba.user.id}",
            {
                "type": "send_notification",
                "message": f"Radni nalog '{radni_nalog.naziv_naloga}' je kreiran.",
            },
        )


class RadniNalogListCreateAPIView(generics.ListCreateAPIView):
    queryset = RadniNalog.objects.all()
    serializer_class = RadniNalogSerializer
    permission_classes = [IsAuthenticated]


class RadniNalogRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RadniNalog.objects.all()
    serializer_class = RadniNalogSerializer
    permission_classes = [IsAuthenticated]


# ==============================
# 2️⃣ API za ocjene kvalitete
# ==============================
class ListaOcjenaKvaliteteAPIView(generics.ListAPIView):
    serializer_class = OcjenaKvaliteteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        radni_nalog_id = self.kwargs.get("radni_nalog_id")
        return OcjenaKvalitete.objects.filter(
            radni_nalog_id=radni_nalog_id, is_active=True
        )


class KreirajOcjenuKvaliteteAPIView(generics.CreateAPIView):
    queryset = OcjenaKvalitete.objects.all()
    serializer_class = OcjenaKvaliteteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        ocjena = serializer.save()
        log_action(self.request.user, ocjena, "CREATE")
        # Slanje notifikacije putem Channels ako je potrebno
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifikacije_{ocjena.radni_nalog.odgovorna_osoba.user.id}",
            {
                "type": "send_notification",
                "message": f"Ocjena kvalitete za radni nalog '{ocjena.radni_nalog.naziv_naloga}' je dodana.",
            },
        )


# ==============================
# 3️⃣ Pregled medija
# ==============================
class PregledMedijaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, medij_tip):
        ocjena = get_object_or_404(OcjenaKvalitete, pk=pk)
        if medij_tip == "slike" and ocjena.slike:
            mime_type = ocjena.slike.file.content_type
            return FileResponse(ocjena.slike.open(), content_type=mime_type)
        elif medij_tip == "video" and ocjena.video:
            mime_type = ocjena.video.file.content_type
            return FileResponse(ocjena.video.open(), content_type=mime_type)
        return Response({"error": "Medij nije dostupan."}, status=404)


# ==============================
# 4️⃣ API za CAD dokumente
# ==============================
class CADDocumentListCreateAPIView(generics.ListCreateAPIView):
    queryset = CADDocument.objects.all()
    serializer_class = CADDocumentSerializer
    permission_classes = [IsAuthenticated]


class CADDocumentDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CADDocument.objects.all()
    serializer_class = CADDocumentSerializer
    permission_classes = [IsAuthenticated]
