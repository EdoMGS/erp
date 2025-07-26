from django.core.management.base import BaseCommand
from nalozi.models import Osoba, Projekt, RadniNalog


class Command(BaseCommand):
    help = "Unosi radne naloge od 51 do 68 u projekt Cisterna Sarajevo"

    def handle(self, *args, **kwargs):
        try:
            projekt = Projekt.objects.get(id=1)
            self.stdout.write(self.style.SUCCESS(f"Pronađen projekt: {projekt.naziv_projekta}"))

            # Radni nalozi od 51 do 68
            radni_nalozi_data = [
                {
                    "naziv": "Izrada T komada za kanistre",
                    "opis": "Izrada T komada za punjenje kanistara",
                    "odgovorna_osoba": "Siniša Trbović",
                    "zadužena_osoba": "Ive Bačić",
                    "rok_za_dobavu": "2025-01-01",
                    "rok_za_izradu": "2025-01-02",
                },
                {
                    "naziv": "Izrada srednjetlačnog cjevovoda vitla",
                    "opis": "Izrada cjevovoda za srednji tlak vitla",
                    "odgovorna_osoba": "Milan Potkonjak",
                    "zadužena_osoba": "Samuel",
                    "rok_za_dobavu": "2025-01-03",
                    "rok_za_izradu": "2025-01-04",
                },
                {
                    "naziv": "Izrada visokotlačnog cjevovoda vitla",
                    "opis": "Izrada visokotlačnog cjevovoda za vitlo",
                    "odgovorna_osoba": "Renato Habijanec",
                    "zadužena_osoba": "Danijel",
                    "rok_za_dobavu": "2025-01-05",
                    "rok_za_izradu": "2025-01-06",
                },
                {
                    "naziv": "Izrada visokotlačnog cjevovoda H",
                    "opis": "Izrada visokotlačnog cjevovoda H",
                    "odgovorna_osoba": "Siniša Trbović",
                    "zadužena_osoba": "Mario Miletić",
                    "rok_za_dobavu": "2025-01-07",
                    "rok_za_izradu": "2025-01-08",
                },
                {
                    "naziv": "Montaža vitla",
                    "opis": "Montaža vitla na konstrukciju",
                    "odgovorna_osoba": "Ive Bačić",
                    "zadužena_osoba": "Milan Potkonjak",
                    "rok_za_dobavu": "2025-01-09",
                    "rok_za_izradu": "2025-01-10",
                },
                {
                    "naziv": "Nabava inox materijala",
                    "opis": "Nabava i skladištenje inox materijala za projekt",
                    "odgovorna_osoba": "Mario Miletić",
                    "zadužena_osoba": "Renato Habijanec",
                    "rok_za_dobavu": "2025-01-11",
                    "rok_za_izradu": "2025-01-12",
                },
                {
                    "naziv": "Nabava gumenih dijelova",
                    "opis": "Nabava gumenih dijelova i prirubnica",
                    "odgovorna_osoba": "Siniša Trbović",
                    "zadužena_osoba": "Mijah",
                    "rok_za_dobavu": "2025-01-13",
                    "rok_za_izradu": "2025-01-14",
                },
                {
                    "naziv": "Nabava spojnica",
                    "opis": "Nabava spojnica za cjevovod",
                    "odgovorna_osoba": "Renato Habijanec",
                    "zadužena_osoba": "Samuel",
                    "rok_za_dobavu": "2025-01-15",
                    "rok_za_izradu": "2025-01-16",
                },
                {
                    "naziv": "Nabava ventila i pneumatike",
                    "opis": "Nabava ventila i pneumatskih komponenti",
                    "odgovorna_osoba": "Milan Potkonjak",
                    "zadužena_osoba": "Ive Bačić",
                    "rok_za_dobavu": "2025-01-17",
                    "rok_za_izradu": "2025-01-18",
                },
                {
                    "naziv": "Nabava kompenzatora",
                    "opis": "Nabava kompenzatora za cjevovod",
                    "odgovorna_osoba": "Siniša Trbović",
                    "zadužena_osoba": "Danijel",
                    "rok_za_dobavu": "2025-01-19",
                    "rok_za_izradu": "2025-01-20",
                },
                {
                    "naziv": "Izrada kontrolne ploče",
                    "opis": "Izrada kontrolne ploče za sustav",
                    "odgovorna_osoba": "Renato Habijanec",
                    "zadužena_osoba": "Milan Potkonjak",
                    "rok_za_dobavu": "2025-01-21",
                    "rok_za_izradu": "2025-01-22",
                },
                {
                    "naziv": "Nabava nivokaza",
                    "opis": "Nabava nivokaza za mjerenje razine",
                    "odgovorna_osoba": "Siniša Trbović",
                    "zadužena_osoba": "Mario Miletić",
                    "rok_za_dobavu": "2025-01-23",
                    "rok_za_izradu": "2025-01-24",
                },
                {
                    "naziv": "Izrada konstrukcije kontrolne ploče",
                    "opis": "Izrada konstrukcije za kontrolnu ploču",
                    "odgovorna_osoba": "Milan Potkonjak",
                    "zadužena_osoba": "Samuel",
                    "rok_za_dobavu": "2025-01-25",
                    "rok_za_izradu": "2025-01-26",
                },
                {
                    "naziv": "Elektrospajanje kontrolne ploče",
                    "opis": "Elektrospajanje kontrolne ploče na sustav",
                    "odgovorna_osoba": "Renato Habijanec",
                    "zadužena_osoba": "Siniša Trbović",
                    "rok_za_dobavu": "2025-01-27",
                    "rok_za_izradu": "2025-01-28",
                },
                {
                    "naziv": "Oprema",
                    "opis": "Izrada nosača i instalacija opreme",
                    "odgovorna_osoba": "Mario Miletić",
                    "zadužena_osoba": "Ive Bačić",
                    "rok_za_dobavu": "2025-01-29",
                    "rok_za_izradu": "2025-01-30",
                },
                {
                    "naziv": "Signalizacija - montaža",
                    "opis": "Montaža i instalacija signalizacije",
                    "odgovorna_osoba": "Danijel",
                    "zadužena_osoba": "Siniša Trbović",
                    "rok_za_dobavu": "2025-01-31",
                    "rok_za_izradu": "2025-02-01",
                },
            ]

            for zadatak_data in radni_nalozi_data:
                odgovorna_osoba = Osoba.objects.filter(ime=zadatak_data["odgovorna_osoba"]).first()
                zadužena_osoba = Osoba.objects.filter(ime=zadatak_data["zadužena_osoba"]).first()

                if odgovorna_osoba and zadužena_osoba:
                    nalog = RadniNalog.objects.create(
                        projekt=projekt,
                        naziv_naloga=zadatak_data["naziv"],
                        opis=zadatak_data["opis"],
                        odgovorna_osoba=odgovorna_osoba,
                        zadužena_osoba=zadužena_osoba,
                        rok_za_dobavu=zadatak_data["rok_za_dobavu"],
                        rok_za_izradu=zadatak_data["rok_za_izradu"],
                        status="Planirano",  # Početni status
                    )
                    self.stdout.write(self.style.SUCCESS(f"Radni nalog '{nalog.naziv_naloga}' uspješno kreiran."))
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Osoba '{zadatak_data['odgovorna_osoba']}' ili '{zadatak_data['zadužena_osoba']}' ne postoji."
                        )
                    )

        except Projekt.DoesNotExist:
            self.stdout.write(self.style.ERROR("Projekt s ID-om 1 nije pronađen."))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Dogodila se greška: {e}"))
