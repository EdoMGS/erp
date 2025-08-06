from django.http import FileResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Materijal, OcjenaKvalitete, Projekt, RadniNalog, TehnickaDokumentacija
from .serializers import (
    MaterijalSerializer,
    OcjenaKvaliteteSerializer,
    ProjektSerializer,
    RadniNalogSerializer,
    TehnickaDokumentacijaSerializer,
)
from .utils import informiraj_ocjenjivace, log_action


# -------- 1. API za radne naloge -------- #
class ListaRadnihNalogaAPIView(generics.ListAPIView):
    queryset = RadniNalog.objects.filter(is_active=True)
    serializer_class = RadniNalogSerializer
    permission_classes = [IsAuthenticated]


class DetaljiRadnogNalogaAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = RadniNalog.objects.filter(is_active=True)
    serializer_class = RadniNalogSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        radni_nalog = serializer.save()
        log_action(self.request.user, radni_nalog, "UPDATE")


class KreirajRadniNalogAPIView(generics.CreateAPIView):
    queryset = RadniNalog.objects.all()
    serializer_class = RadniNalogSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        radni_nalog = serializer.save()
        informiraj_ocjenjivace(radni_nalog)
        log_action(self.request.user, radni_nalog, "CREATE")


# -------- 2. API za ocjene kvalitete -------- #
class ListaOcjenaKvaliteteAPIView(generics.ListAPIView):
    serializer_class = OcjenaKvaliteteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        radni_nalog_id = self.kwargs.get("radni_nalog_id")
        return OcjenaKvalitete.objects.filter(radni_nalog_id=radni_nalog_id, is_active=True)


class KreirajOcjenuKvaliteteAPIView(generics.CreateAPIView):
    queryset = OcjenaKvalitete.objects.all()
    serializer_class = OcjenaKvaliteteSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        ocjena = serializer.save()
        log_action(self.request.user, ocjena, "CREATE")


# -------- 3. API za projekte -------- #
class ListaProjekataAPIView(generics.ListAPIView):
    queryset = Projekt.objects.filter(is_active=True)
    serializer_class = ProjektSerializer
    permission_classes = [IsAuthenticated]


class DetaljiProjektaAPIView(generics.RetrieveAPIView):
    queryset = Projekt.objects.filter(is_active=True)
    serializer_class = ProjektSerializer
    permission_classes = [IsAuthenticated]


class StatistikaProjektaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, projekt_id):
        projekt = get_object_or_404(Projekt, id=projekt_id, is_active=True)
        return Response(
            {
                "napredak": projekt.napredak,
                "status": projekt.status,
                "ukupni_radni_nalozi": projekt.radni_nalozi.count(),
                "prosjek_ocjena": projekt.radni_nalozi.aggregate(avg_ocjena=Avg("ocjene_kvalitete__ocjena"))[
                    "avg_ocjena"
                ],
            }
        )


# -------- 4. API za materijale -------- #
class ListaMaterijalaAPIView(generics.ListAPIView):
    queryset = Materijal.objects.filter(is_active=True)
    serializer_class = MaterijalSerializer
    permission_classes = [IsAuthenticated]


class DetaljiMaterijalaAPIView(generics.RetrieveAPIView):
    queryset = Materijal.objects.filter(is_active=True)
    serializer_class = MaterijalSerializer
    permission_classes = [IsAuthenticated]


# -------- 5. API za tehničku dokumentaciju -------- #
class ListaTehnickeDokumentacijeAPIView(generics.ListAPIView):
    queryset = TehnickaDokumentacija.objects.filter(is_active=True)
    serializer_class = TehnickaDokumentacijaSerializer
    permission_classes = [IsAuthenticated]


class DetaljiTehnickeDokumentacijeAPIView(generics.RetrieveAPIView):
    queryset = TehnickaDokumentacija.objects.filter(is_active=True)
    serializer_class = TehnickaDokumentacijaSerializer
    permission_classes = [IsAuthenticated]


# -------- 6. Pregled medija u ocjenama -------- #
class PregledMedijaAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, medij_tip):
        ocjena = get_object_or_404(OcjenaKvalitete, pk=pk)
        if medij_tip == "slike" and ocjena.slike:
            return FileResponse(ocjena.slike.open(), content_type="image/jpeg")
        elif medij_tip == "video" and ocjena.video:
            return FileResponse(ocjena.video.open(), content_type="video/mp4")
        return Response({"error": "Medij nije dostupan."}, status=404)
