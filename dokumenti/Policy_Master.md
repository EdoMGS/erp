# Policy Master

Ovaj dokument objedinjuje i ažurira sve interne pravilnike i upute prema novom lean‑ERP modelu.

## 1. Welcome Pack

Ovaj dokument korisnicima (radnicima i menadžerima) predstavlja osnovne korake i principe korištenja ERP‑a:

### 1.1. Uvod i misija
- Kratki opis “Tvornice love” i Lean‑ERP
- Cilj: transparentnost prihoda i motivacija radnika po profitu

### 1.2. Real‑Time Dashboard i Boje Statusa
- **Crveno**: pool < suma minimalca + (stanarina za strane radnike) + PROFIT_FLOOR
- **Žuto**: pool pokriva minimalac + (stanarina za strane radnike), ali ne i bonus
- **Zeleno**: pool > minimalac + (stanarina za strane radnike) + bonus; slobodni radni sati
- Widget “My Profit”: prikaz minimalca, bonusa, ukupnog neto

### 1.3. Ponuda i Prihvaćanje
1. Izrada ponude:
   - Unesi tip posla (npr. Farbanje auta)
   - Definiraj količinu (m² ili kom)
   - Odaberi faktore (Complexity, FinishType, Urgency)
   - ERP izračunava cijenu i prikazuje breakdown
2. Slanje ponude:
   - Generira se PDF + link “Prihvati”
3. Prihvaćanje:
   - Kupac potvrđuje → kreira se Job u ERP‑u

### 1.4. Radnički UX Flow (kiosk)
1. **Login**: QR kod + PIN/fingerprint
2. **Start Job**: odabir kreiranog Joba iz liste
3. **Work in progress**: status “U radu”
4. **QC i foto‑upload**:
   - Lean QC lista (5 checkpointa)
   - Foto dokumentacija prije/poslije
5. **Završetak**: klik “Complete” → Invoice + Payroll proces pokreće se automatski

## 2. Opći pravilnik o radu

Ovaj pravilnik definira interne procedure i pravila ponašanja na radnom mjestu u skladu s ERP‑om.

### 2.1. Postojeće sekcije
- Radno vrijeme i pauze
- Prijava i odjava rada
- Pravila disciplinskog sustava

### 2.2. Što mijenjamo
1. **Elektronička prijava/odjava**
   - Umjesto papirnatih lista, radnik koristi kiosk:
     - **Login**: QR kod + PIN/fingerprint
     - Prijava rada: klik "Start"
     - Odjava rada: klik "Stop"
2. **Radni nalozi i izvještaji**
   - Svi poslovi se pokreću i zatvaraju u ERP aplikaciji
   - Ručni popisi i Excel tablice se brišu
3. **My Profit widget**
   - Dodaje se na glavni ekran:
     - Pregled minimalca, stanarine (samo za strane radnike), bonusa
     - Graf kreditnog stanja stabilizacijskog fonda
4. **Disciplinski sustav**
   - Automatizirani alerti za QC‑fail rate > 20%
   - Evidencija rework‑a i penalizacija unutar ERP‑a
5. **Komunikacija i podrška**
   - Svi upiti šalju se kroz ERP tickete (modul `common/support`)
   - Integracija s chatom/Slackom za brzu notifikaciju menadžerima

## 3. Profit‑Share Pravilnik

Ovaj pravilnik definira način raspodjele prihoda fakture među kompanijom, fondom i radnicima.

### 3.1. Postojeće sekcije
- **Fiksni profit floor**: dosada je postojala fiksna sigurnosna marža od 2.000 € koja se prije podjele zadržavala u sustavu za hitne potrebe.
- **Share postotci**: standardna raspodjela bila je 50 % za kompaniju, 20 % za stabilizacijski fond i 30 % za radnike.

### 3.2. Što mijenjamo
- **Dynamic Profit Floor**:
  - Umjesto fiksnih 2.000 €, uvodimo automatski izračun 10 % od Company share, s maksimalnom granicom (cap) od 2.000 € mjesečno.
  - Time se rezerva prilagođava rastu prihoda i ne opterećuje početne faze.
- **Ramp‑up faza**:
  - Za prva 3 mjeseca (ili dok se ne pokriju fiksni troškovi + baseline pool) koristimo raspodjelu 40 / 40 / 20 umjesto 50/20/30.
- **ProfitPoints**:
  - Radnički dio (preostali 30 %) dijeli se prema bodovima dodijeljenim po tipu i kvaliteti posla, umjesto klasične raspodjele po satu.

## 4. Stabilizacijski fond

Ovaj modul definira kako se upravlja i koristi stabilizacijski fond (Fund).

### 4.1. Postojeće sekcije
- Fiksni fond za hitne troškove: ranije je bio definiran fiksni iznos bez jasnih pravila akumulacije i korištenja.

### 4.2. Što mijenjamo
1. **Fund_pct**
   - Umjesto fiksnog iznosa, fond se puni sa **20 % od iznosa svake fakture**.
2. **Prioritet alokacije**
   - Prvo se fond koristi za **nadoknadu manjkova pool‑a** i minimalne plaće (bruto minimalac + employer doprinosi).
   - Zatim pokriva troškove hitnih situacija: neočekivane popravke, servis opreme.
3. **Pravila korištenja**
   - **Rework penalizacija**: QC‑fail rate > 20 % smanjuje automatski fund share za naredni period.
   - **Odobrenje za veće izdatke**: iznad 1 000 € trošak se odobrava od strane menadžmenta.
4. **Transparentnost**
   - Svaki “Fund transaction” generira **JournalEntry** i prikazuje se na menadžerskom dashboardu.
   - Radnici vide samo stanje dostupnog fonda, ne pojedinačne transakcije.

## 5. GDPR Pravilnik

Ovaj pravilnik definira pravila za zaštitu osobnih podataka unutar ERP sustava.

### 5.1. Postojeće sekcije
- Opće odredbe o zaštiti osobnih podataka i prava ispitanika

### 5.2. Što mijenjamo
1. **Politika retencije fotografija QC**
   - Pohrana fotografija generiranih u QC modulu zadržava se **6 mjeseci**, nakon čega se automatski brišu.
2. **Zahtjev za brisanje / pristup**
   - Radnik može kroz ERP otvoriti ticket u `common/support` modulu s opcijom “Zahtjev za izbrisati podatke”.
   - Data Protection Officer (DPO) prima notifikaciju i obrađuje zahtjev.
3. **Evidencija suglasnosti**
   - Prilikom prvog logina, radnik mora potvrditi suglasnost za obradu fotografija i osobnih podataka.
   - Sustav automatski generira zapis u `gdpr_consent` tablici s datumom i vremenskom oznakom.
4. **Sigurnosne mjere**
   - Fotografije se pohranjuju u enkriptiranu S3 bucket (ili lokalni equivalent) s kontrolom pristupa.
   - Svi zahtjevi za izvoz/brisanje osobnih podataka prate se kroz audit log.

**Sljedeći koraci:**
1. Finalni proofread svih sekcija
2. Generiranje PDF i Word verzije
3. Pohrana u `dokumenta/Policy_Master.md`
