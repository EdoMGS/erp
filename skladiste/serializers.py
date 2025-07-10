from rest_framework import serializers

from .models import (
    Alat,
    Artikl,
    DnevnikDogadaja,
    HTZOprema,
    Lokacija,
    Materijal,
    SkladisteResurs,
    Zona,
)


class ZonaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zona
        fields = "__all__"


class LokacijaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lokacija
        fields = "__all__"


class ArtiklSerializer(serializers.ModelSerializer):
    class Meta:
        model = Artikl
        fields = [
            "id",
            "naziv",
            "sifra",
            "trenutna_kolicina",
            "min_kolicina",
            "nabavna_cijena",
            "prodajna_cijena",
            "jedinica_mjere",
            "lokacija",
            "kategorija",
            "dobavljac",
            "is_active",
        ]


class SkladisteResursSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkladisteResurs
        fields = "__all__"


class MaterijalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Materijal
        fields = [
            "id",
            "artikl",
            "radni_nalog",
            "status",
            "tehnicki_nacrt",
            "narudzbenica",
        ]


class AlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Alat
        fields = "__all__"


class HTZOpremaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HTZOprema
        fields = "__all__"


class DnevnikDogadajaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DnevnikDogadaja
        fields = "__all__"
