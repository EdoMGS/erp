import os

import pandas as pd

# Postavite osnovnu putanju gdje su Excel datoteke
BASE_FOLDER = r"D:\MGS-Davor\d$\192.168.1.61\d$\Arhiva MG\arhiva - 2\MG Rijeka docs"
OUTPUT_FILE = "extracted_work_orders.csv"


# Funkcija za pronalazak tablica u Excelu
def find_valid_table(df):
    for i in range(len(df)):
        # Tražimo retke gdje su prisutni željeni stupci
        if all(col in df.iloc[i].values for col in ["NAZIV", "RAD(h)", "IDE"]):
            return df.iloc[i + 1 :]  # Tablica počinje odmah nakon ovog retka
    return None


# Funkcija za izdvajanje relevantnih podataka iz Excel datoteka
def extract_relevant_data(file_path):
    try:
        # Učitaj sve sheetove iz Excel datoteke
        excel_data = pd.ExcelFile(file_path)
        relevant_data = []
        for sheet in excel_data.sheet_names:
            df = excel_data.parse(sheet, header=None)  # Učitaj sve bez zaglavlja
            valid_table = find_valid_table(df)
            if valid_table is not None:
                # Postavljamo nove nazive stupaca i filtriramo potrebne
                valid_table.columns = df.iloc[valid_table.index[0] - 1].values
                relevant_data.append(
                    valid_table[["IDE", "NAZIV", "RAD(h)", "MATERIJAL", "OPREMA"]]
                )
        return pd.concat(relevant_data, ignore_index=True) if relevant_data else None
    except Exception as e:
        print(f"Greška pri obradi datoteke {file_path}: {e}")
        return None


# Funkcija za pretraživanje Excel datoteka u folderima
def search_excel_files(base_folder):
    extracted_data = []
    for root, dirs, files in os.walk(base_folder):
        for file in files:
            if file.endswith((".xls", ".xlsx")):
                file_path = os.path.join(root, file)
                print(f"Obrađujem: {file_path}")
                data = extract_relevant_data(file_path)
                if data is not None:
                    extracted_data.append(data)
    return pd.concat(extracted_data, ignore_index=True) if extracted_data else None


def main():
    # Pretraži i izvuci podatke iz Excel datoteka
    extracted_data = search_excel_files(BASE_FOLDER)
    if extracted_data is not None:
        # Spremi u CSV
        extracted_data.to_csv(OUTPUT_FILE, index=False)
        print(f"Podaci su spremljeni u {OUTPUT_FILE}")
    else:
        print("Nema podataka za izdvajanje.")


if __name__ == "__main__":
    main()
