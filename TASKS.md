### 🧱 TEMELJI ERP-a: MODELI I STRUKTURA PODATAKA

Cilj: Postaviti sve ključne modele koji čine temelj poslovanja i omogućuju višefirmno (multi-tenant) poslovanje.

---

#### 1. `Company` (Tenant)
- `name`, `oib`, `vat_id`, `address`, `city`, `country`, `currency`, `founded_at`, `active`
- `created_at`, `updated_at`
- povezan sa korisnicima i zaposlenicima

#### 2. `BaseModel`
- Abstraktna klasa za nasljeđivanje
- `created_at`, `updated_at`, `created_by`, `updated_by`
- Svaki model mora nasljeđivati ovaj

#### 3. `Employee`
- `user` (FK prema auth.User)
- `company` (FK → Tenant)
- `first_name`, `last_name`, `oib`, `iban`, `role`
- `salary_base`, `active`, `joined_at`, `left_at`
- `cost_center_code` (za povezivanje s financijama)
- `is_foreign` (za smještaj i specijalne dodatke)

#### 4. `CostCenter`
- `code`, `description`, `type` (radnik, vozilo, alat, prostor), `company`
- koristi se za klasifikaciju troškova u knjiženju

#### 5. `Account`
- `code`, `name`, `type` (asset/liability/expense/income), `company`
- koristi se za knjiženje po kontima

#### 6. `AppSetting` (opcionalno)
- `key`, `value`, `company`
- globalna konfiguracija po firmi (npr. minimalac, valuta, porezne stope...)

---

📌 Sve modele smjestiti u:
- `core/models.py` → Company, BaseModel, AppSetting
- `accounts/models.py` → Employee, CostCenter, Account

🧪 Nakon toga:
```bash
python manage.py makemigrations
python manage.py migrate
