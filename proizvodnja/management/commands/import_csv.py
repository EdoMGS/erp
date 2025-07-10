import csv

from django.core.management.base import BaseCommand

from proizvodnja.models import GrupaPoslova, TipProjekta, TipVozila


class Command(BaseCommand):
    help = "Import data from CSV files into the database"

    def add_arguments(self, parser):
        parser.add_argument("--tipvozila", type=str, help="Path to tipvozila.csv file")
        parser.add_argument(
            "--tipprojekta", type=str, help="Path to tipprojekta.csv file"
        )
        parser.add_argument(
            "--grupaposlova", type=str, help="Path to grupaposlova.csv file"
        )

    def handle(self, *args, **options):
        if options["tipvozila"]:
            self.import_tipvozila(options["tipvozila"])
        if options["tipprojekta"]:
            self.import_tipprojekta(options["tipprojekta"])
        if options["grupaposlova"]:
            self.import_grupaposlova(options["grupaposlova"])

    def import_tipvozila(self, file_path):
        try:
            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile, delimiter=";")
                for row in reader:
                    TipVozila.objects.update_or_create(
                        id=row["id"],
                        defaults={
                            "naziv": row["naziv"],
                            "opis": row["opis"],
                            "aktivan": row["aktivan"] == "t",
                        },
                    )
            self.stdout.write(self.style.SUCCESS("Successfully imported TipVozila"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing TipVozila: {e}"))

    def import_tipprojekta(self, file_path):
        try:
            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile, delimiter=";")
                for row in reader:
                    TipProjekta.objects.update_or_create(
                        id=row["id"],
                        defaults={
                            "naziv": row["naziv"],
                            "opis": row["opis"],
                            "aktivan": row["aktivan"] == "t",
                        },
                    )
            self.stdout.write(self.style.SUCCESS("Successfully imported TipProjekta"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing TipProjekta: {e}"))

    def import_grupaposlova(self, file_path):
        try:
            with open(file_path, newline="", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile, delimiter=";")
                for row in reader:
                    GrupaPoslova.objects.update_or_create(
                        id=row["id"],
                        defaults={
                            "naziv": row["naziv"],
                            "opis": row["opis"],
                            "tip_projekta_id": row["tip_projekta_id"],
                        },
                    )
            self.stdout.write(self.style.SUCCESS("Successfully imported GrupaPoslova"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing GrupaPoslova: {e}"))
