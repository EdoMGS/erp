import csv
import json
import os
import sys

import django
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from skladiste.models import Artikl, DnevnikDogadaja, Lokacija

# Postavljanje Django okruženja
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_root.settings.dev')
django.setup()

sys.stdout.reconfigure(encoding='utf-8')


# 1. Premještanje artikala između lokacija
@csrf_exempt
@login_required
@permission_required('skladiste.change_artikl', raise_exception=True)
def premjesti_artikl(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        artikl = get_object_or_404(Artikl, id=data.get('artikl_id'))
        nova_lokacija = get_object_or_404(Lokacija, id=data.get('nova_lokacija_id'))

        with transaction.atomic():
            stara_lokacija = artikl.lokacija
            artikl.lokacija = nova_lokacija
            artikl.save()

            DnevnikDogadaja.objects.create(
                poruka=f"Artikl '{artikl.naziv}' premješten iz '{stara_lokacija.naziv}' u '{nova_lokacija.naziv}'",
                tip='info',
            )
        return JsonResponse({'status': 'success', 'poruka': f"Artikl '{artikl.naziv}' uspješno premješten."})
    return HttpResponse(status=405)


# 2. Rezervacija artikala za potrebe drugih modula
@csrf_exempt
@login_required
@permission_required('skladiste.change_artikl', raise_exception=True)
def rezerviraj_artikl(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        artikl = get_object_or_404(Artikl, id=data.get('artikl_id'))
        kolicina = data.get('kolicina')

        if artikl.kolicina >= kolicina:
            artikl.kolicina -= kolicina
            artikl.status = 'rezervirano'
            artikl.save()

            DnevnikDogadaja.objects.create(
                poruka=f"Rezervirano {kolicina} jedinica artikla '{artikl.naziv}' za narudžbu/projekt.", tip='info'
            )
            return JsonResponse(
                {'status': 'success', 'poruka': f"Rezervirano {kolicina} jedinica artikla '{artikl.naziv}'."}
            )
        else:
            return JsonResponse({'status': 'error', 'poruka': 'Nema dovoljno zaliha za rezervaciju.'})
    return HttpResponse(status=405)


# 3. API za provjeru dostupnosti artikala (za druge module)
@csrf_exempt
@login_required
@permission_required('skladiste.view_artikl', raise_exception=True)
def provjeri_dostupnost(request):
    if request.method == 'GET':
        artikl_id = request.GET.get('artikl_id')
        artikl = get_object_or_404(Artikl, id=artikl_id)
        return JsonResponse({'naziv': artikl.naziv, 'kolicina': artikl.kolicina, 'status': artikl.status})
    return HttpResponse(status=405)


# 4. Automatizacija premještanja zaliha ako su ispod minimalne razine
def automatizirano_premjestanje():
    minimalna_kolicina = 10
    artikli = Artikl.objects.filter(kolicina__lt=minimalna_kolicina, status='u_skladištu')
    for artikl in artikli:
        alternativne_lokacije = Lokacija.objects.exclude(id=artikl.lokacija.id)
        if alternativne_lokacije.exists():
            nova_lokacija = alternativne_lokacije.first()
            stara_lokacija = artikl.lokacija
            artikl.lokacija = nova_lokacija
            artikl.save()
            DnevnikDogadaja.objects.create(
                poruka=f"Automatski premještaj: Artikl '{artikl.naziv}' premješten iz '{stara_lokacija.naziv}' u '{nova_lokacija.naziv}' zbog niske zalihe.",
                tip='upozorenje',
            )


# 5. Integracija s ostalim modulima - primjer funkcije za nabavu
def obavijesti_nabavu_o_niskim_zalihama():
    minimalna_kolicina = 10
    artikli = Artikl.objects.filter(kolicina__lt=minimalna_kolicina, status='u_skladištu')
    for artikl in artikli:
        # Ovdje bi bila logika za slanje zahtjeva modulu nabave
        print(f"Obavijest nabavi: Artikl '{artikl.naziv}' ima niske zalihe ({artikl.kolicina} jedinica).")


# 6. Unos artikala putem CSV datoteke
def unos_artikala_csv(putanja_do_datoteke):
    try:
        with open(putanja_do_datoteke, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            with transaction.atomic():
                for red in reader:
                    lokacija, kreirano = Lokacija.objects.get_or_create(naziv=red['lokacija'])
                    Artikl.objects.create(
                        naziv=red['naziv'],
                        kolicina=int(red['kolicina']),
                        lokacija=lokacija,
                        datum_isteka=red.get('datum_isteka') or None,
                        serijski_broj=red.get('serijski_broj') or None,
                        status=red.get('status', 'u_skladištu'),
                    )
        print("Artikli uspješno uneseni iz CSV datoteke.")
    except FileNotFoundError:
        print("Greška: Datoteka nije pronađena.")
    except ValidationError as e:
        print(f"Greška prilikom validacije podataka: {e}")
    except Exception as e:
        print(f"Greška prilikom unosa artikala: {e}")


# 7. Home stranica skladišta
def skladiste_home(request):
    return render(request, 'skladiste/home.html')


# 8. URL konfiguracija
urlpatterns = [
    path('', skladiste_home, name='skladiste_home'),
    path('artikli/', provjeri_dostupnost, name='popis_artikala'),
    path('dodaj_artikl/', rezerviraj_artikl, name='dodaj_artikl'),
    path('premjesti_artikl/', premjesti_artikl, name='premjesti_artikl'),
]


# 9. Komanda za inicijalizaciju skladišta
class Command(BaseCommand):
    help = 'Inicijalizacija skladišta'

    def handle(self, *args, **kwargs):
        try:
            # Dodavanje nove lokacije
            lokacija = Lokacija.objects.create(naziv="Centralno Skladište")
            self.stdout.write(self.style.SUCCESS(f"Lokacija dodana: {lokacija}"))

            # Dodavanje novog artikla
            artikl = Artikl.objects.create(naziv="Novi Proizvod", kolicina=5, lokacija=lokacija)
            self.stdout.write(self.style.SUCCESS(f"Artikl dodan: {artikl}"))

            # Testiranje rezervacije
            rezerviraj_artikl_request = type(
                'Request',
                (object,),
                {
                    "method": "POST",
                    "body": json.dumps({"artikl_id": artikl.id, "kolicina": 3}),
                    "user": User.objects.first(),
                },
            )
            self.stdout.write(rezerviraj_artikl(rezerviraj_artikl_request).content.decode())

            # Testiranje automatiziranog premještanja
            automatizirano_premjestanje()

            # Obavijesti nabavu o niskim zalihama
            obavijesti_nabavu_o_niskim_zalihama()

            # Testiranje unosa u dnevnik događaja
            korisnik = User.objects.first()
            if korisnik:
                DnevnikDogadaja.objects.create(korisnik=korisnik, poruka="Testiranje unosa u dnevnik", tip="info")
                self.stdout.write(self.style.SUCCESS("Dnevnik dogadaja ažuriran."))

            # Testiranje unosa artikala putem CSV datoteke
            unos_artikala_csv("artikli.csv")

            self.stdout.write(self.style.SUCCESS("Proširene funkcionalnosti uspješno testirane."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Dogodila se greška: {e}"))
