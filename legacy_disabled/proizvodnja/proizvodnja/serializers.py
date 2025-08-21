# proizvodnja/serializers.py

from django.contrib.auth import get_user_model
from rest_framework import serializers

# Uvoz modela iz drugih aplikacija:
# from skladiste.models import Materijal
from financije.serializers import FinancialDetailsSerializer
from financije.services import calculate_project_costs
from ljudski_resursi.serializers import EmployeeSerializer

from .models import (  # Remove Nagrada from imports; Oprema,  # Removed Oprema; RadniProces,  # Removed RadniProces; AnotherModel,  # Removed AnotherModel
    Angazman,
    DodatniAngazman,
    GrupaPoslova,
    MonthlyWorkRecord,
    Notifikacija,
    OcjenaKvalitete,
    PovijestPromjena,
    ProizvodniResurs,
    Proizvodnja,
    Projekt,
    RadniNalog,
    RadniNalogMaterijal,
    TemplateRadniNalog,
    TipProjekta,
    TipVozila,
    Usteda,
    VideoMaterijal,
    VideoPitanje,
)

User = get_user_model()


class TipProjektaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipProjekta
        fields = "__all__"


class TipVozilaSerializer(serializers.ModelSerializer):
    class Meta:
        model = TipVozila
        fields = "__all__"


class GrupaPoslovaSerializer(serializers.ModelSerializer):
    class Meta:
        model = GrupaPoslova
        fields = "__all__"


class ProjektSerializer(serializers.ModelSerializer):
    tip_projekta = TipProjektaSerializer()
    tip_vozila = TipVozilaSerializer()
    financial_details = FinancialDetailsSerializer()
    financials = serializers.SerializerMethodField()

    def get_financials(self, obj):
        return calculate_project_costs(obj)

    class Meta:
        model = Projekt
        fields = "__all__"


class RadniNalogMaterijalSerializer(serializers.ModelSerializer):
    # materijal = MaterijalSerializer() # ako imaš definiran MaterijalSerializer u skladiste
    class Meta:
        model = RadniNalogMaterijal
        fields = "__all__"


class RadniNalogSerializer(serializers.ModelSerializer):
    projekt = ProjektSerializer()
    grupa_posla = GrupaPoslovaSerializer()
    dodatne_osobe = EmployeeSerializer(many=True)
    odgovorna_osoba = EmployeeSerializer()
    # materijali -> moglo bi ići preko nested serializer-a ako treba
    # employee = EmployeeSerializer()

    class Meta:
        model = RadniNalog
        fields = "__all__"


class AngazmanSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer()

    class Meta:
        model = Angazman
        fields = "__all__"


class DodatniAngazmanSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer()

    class Meta:
        model = DodatniAngazman
        fields = "__all__"


class OcjenaKvaliteteSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer()

    class Meta:
        model = OcjenaKvalitete
        fields = "__all__"


# Remove NagradaSerializer class


class VideoMaterijalSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoMaterijal
        fields = "__all__"


class VideoPitanjeSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoPitanje
        fields = "__all__"


class NotifikacijaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notifikacija
        fields = "__all__"


class PovijestPromjenaSerializer(serializers.ModelSerializer):
    class Meta:
        model = PovijestPromjena
        fields = "__all__"


class MonthlyWorkRecordSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer()

    class Meta:
        model = MonthlyWorkRecord
        fields = "__all__"


class UstedaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usteda
        fields = "__all__"


class ProizvodniResursSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProizvodniResurs
        fields = "__all__"


class TemplateRadniNalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateRadniNalog
        fields = "__all__"


class ProizvodnjaSerializer(serializers.ModelSerializer):
    projekt = ProjektSerializer()

    class Meta:
        model = Proizvodnja
        fields = "__all__"
