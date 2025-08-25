# TASKS_KNJIGOVODSTVO.md

## Vizija
ERP mora biti **100% usklađen s važećim zakonodavstvom u RH (2025)**: Zakon o računovodstvu, Zakon/Pravilnik o PDV-u, fiskalizacija/e-Računi (EN 16931), JOPPD.  
Cilj: **sve transakcije** završavaju u glavnoj knjizi (`JournalEntry/Item`), ΣD=ΣC, izvještaji (IRA/URA, PDV-O, P&L, Bilanca, JOPPD) iz baze → “čisto ko suza” kod nadzora.

---

## K0 — Ledger hardening (osnova)
 - [x] `ledger/post_transaction()` – idempotentno; `reverse_entry()`; `posted_at/locked` (period lock = samo reversal).
 - [x] `tenant` polje na svim financijskim modelima + `unique(tenant, number)` na `Account`.
 - [x] `account_map_hr.py` – mapiranje event → konta (sales, advance, purchase, bank, RC, IC-acq, export).
 - [x] Loader: `load_coa_hr_2025()` → fixture `fixtures/hr_coa_2025.json` (razredi 0–9; PDV 14xx/47xx; tipični 12xx/22xx/7xxx/4xxx).
 - [x] **Testovi**: ΣD=ΣC property; idempotency key; lock enforcement; reversal balanced.

---

## K1 — Posting rules (događaji)
 - [x] **Prodajna faktura**: DR 1200 (AR) / CR 76xx (prihod) + CR 47xx (PDV).
 - [x] **Avans kupca**: DR 1000 (banka) / CR 2200 (obveza); **prebijanje**: DR 2200 / CR 1200.
 - [x] **Ulazni račun**: DR 4xxx (trošak) + DR 14xx (pretporez) / CR 22xx (AP).
 - [x] **Banka**: uplata kupca (DR 1000 / CR 1200); isplata dobavljaču (DR 22xx / CR 1000).
 - [x] **RC građevina** (prijenos): DR 4xxx / CR 22xx **+** DR 14xx / CR 47xx (samoporezivanje).
 - [x] **IC stjecanje**: DR 3xxx/4xxx / CR 22xx **+** DR 14xx / CR 47xx.
 - [x] **Izvoz 0%**: DR 1200 / CR 76xx (bez PDV).
 - [x] **Testovi**: parametrizirano po stopama i režimima; balanced; idempotentno.

---

## K2 — Fiskalizacija & e-Računi
- [ ] Modul `fiskalizacija/`:
  - Generator **UBL 2.1 (EN 16931)** iz `Invoice` (OIB, PDV breakdown, PaymentMeans).
  - `gateway.py`: adapter prema Poreznoj/posredniku (sandbox → prod), potpis certifikatom, JIR/ZKI/status pohranjen.
  - PDF: QR + hash footer (snapshot SHA256).
- [ ] Feature flag: `FISKALIZACIJA_ERACUN=True` (datum primjene 2026/2027).
- [ ] **Testovi**: demo račun → UBL → sandbox fiskalizacija → JIR → PDF s QR i hashom.

---

## K3 — PDV engine & knjige
- [x] `VatCode` (stopa; tip: standard/13/5/0/exempt/RC/IC-supply/IC-acq).
- [x] `VatBookSale` (IRA) i `VatBookPurchase` (URA): datum, broj, OIB, osnovice po stopama, iznosi, RC flag, napomene.
- [x] `pdv_o_export.py` – agregacija iz IRA/URA u **PDV-O** (CSV/XML za ePorezna).
- [x] **Pravila**: domaće isporuke; RC građevina (račun bez PDV + napomena članka, samoporezivanje); IC isporuke/stjecanja; izvoz.
- [x] **Testovi**: 5 scenarija (25%, 13%, RC, IC-acq, export) → PDV-O polja i zbrojevi točni ±0.01; IRA/URA = PDV-O.

---

## K4 — HR Payroll & JOPPD
- [x] `PayrollRun` + `PayrollItem`; kalkulator bruto↔neto↔trošak (stope 2025; doprinosi/porez/olaksice).
- [x] Mapping šifri primitaka (rad, bonus, naknade).
- [x] `joppd_xml.py` – export u važeći **JOPPD XML** (trenutni XSD).
- [x] Povezati 30% **profit-share** pool s isplatama (nalog za isplatu + knjiženje).
- [x] **Testovi**: 3 radnika (različiti scenariji); JOPPD prolazi XSD validaciju.

---

## K5 — Izvještaji (audit-ready)
- [x] P&L i Bilanca (light) **iz `JournalItem`** (ne iz `Invoice`).
- [x] IRA/URA ispisi; **PDV-O rekap**; **AR/AP aging**.
- [x] “Related party ledger” (intercompany) s cross-tenant trace-id.
- [x] **Testovi**: consistency – IRA+URA zbrojevi = PDV-O; Bilanca: aktiva = pasiva.

---

## K6 — Compliance & arhiva
- [ ] **Retention**: čuvanje PDF/UBL/JOPPD ≥ 11 g. (WORM; nepromjenjivo).
- [ ] **Audit log**: append-only (DB constraint), hash u footeru PDF-ova.
- [ ] **OIB** validacija na partnerima i dokumentima.
- [ ] **Period lock**: nakon predaje PDV-O/JOPPD izmjene samo reversal.
- [ ] **Testovi**: pokušaj edit nakon lock → fail; audit log je nepromjenjiv.

---

## Definition of Done (v1.0 – “audit-ready”)
- 100% poslovnih događaja ide kroz `post_transaction()`; ručno samo reversal.
- PDV (IRA/URA, PDV-O) generiran iz baze i validan za ePorezna.
- e-Računi (UBL 2.1 + fiskalizacija) spremni za obveznu primjenu.
- JOPPD XML validan po XSD; payroll knjižen u glavnu knjigu.
- Intercompany simetrično knjižen s related-party flagom i audit trailom.
- P&L/Bilanca/PDV/aging izvedeni iz `JournalItem`; period lock na mjesečnoj bazi.

---

## Napomene za implementaciju
- **Zaokruživanje**: `Decimal`, HALF_UP, 2 dec; jedan `money()` helper; property testovi.
- **Napomene na računima** po PDV režimu (npr. RC: “Prijenos porezne obveze – ZPDV, čl. …”).
- **EUR** svugdje; tečajnice samo ako ti trebaju (FX stub).
- **RBAC + tenant filter** default; Idempotency-Key na POST.
