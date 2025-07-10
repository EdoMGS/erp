import csv
from nalozi.models import TipProjekta, GrupaPoslova, TipVozila

# 1. Unos podataka za TipProjekta
def import_tip_projekta(file_path):
    with open(file_path, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')  # Prilagodite razdjelnik ako je drugačiji
        for row in reader:
            try:
                TipProjekta.objects.get_or_create(
                    naziv=row['naziv'],
                    opis=row['opis'],
                    aktivan=row['aktivan'] == 't'
                )
                print(f"Uspješno unesen TipProjekta: {row['naziv']}")
            except Exception as e:
                print(f"Greška pri unosu TipProjekta: {row['naziv']} - {e}")

# 2. Unos podataka za GrupaPoslova
def import_grupa_poslova(file_path):
    import csv
    from nalozi.models import GrupaPoslova, TipProjekta

    with open(file_path, encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')  # Prilagođeni razdjelnik
        for row in reader:
            try:
                # Pronađi odgovarajući TipProjekta prema ID-u
                tip_projekta = TipProjekta.objects.get(id=row['tip_projekta_id'])

                # Kreiraj ili ažuriraj GrupaPoslova
                GrupaPoslova.objects.get_or_create(
                    naziv=row['naziv'],
                    opis=row['opis'],
                    tip_projekta=tip_projekta
                )
                print(f"Uspješno unesena GrupaPoslova: {row['naziv']}")
            except TipProjekta.DoesNotExist:
                print(f"TipProjekta s ID-om '{row['tip_projekta_id']}' ne postoji. Preskočen unos.")
            except Exception as e:
                print(f"Greška pri unosu GrupaPoslova: {row['naziv']} - {e}")


# 3. Unos podataka za TipVozila
def import_tip_vozila(file_path):
    with open(file_path, encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Preskoči header
        for row in reader:
            try:
                TipVozila.objects.get_or_create(
                    naziv=row[1],
                    opis=row[2],
                    aktivan=row[3] == 't'
                )
                print(f"Uspješno unesen TipVozila: {row[1]}")
            except Exception as e:
                print(f"Greška pri unosu TipVozila: {row[1]} - {e}")

# Putanje do CSV datoteka
if __name__ == "__main__":
    import_tip_projekta('C:/Users/38591/Desktop/tipprojekta.csv')
    import_grupa_poslova('C:/Users/38591/Desktop/grupaposlova.csv')
    import_tip_vozila('C:/Users/38591/Desktop/tipvozila.csv')
