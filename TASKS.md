# tasks.md — Copilot 4o **Step‑by‑Step** Backlog

> **Cilj:** Automatizirano (koliko je moguće) očistiti, konsolidirati i nadograditi ERP repo tako da krajem Sprinta 0 projekt diže Docker‑om, prolazi testove i ima početni multi‑tenant kostur. Svaki checkbox je samostalan zadatak koji Visual Studio + Copilot 4o mogu riješiti prompt‑driven pristupom.
>
> **Kako koristiti:**
>
> 1. Otvori ovaj file u Visual Studio‑u.
> 2. Kreni po redu (Task List u VS‑u prepoznaje `- [ ]`).
> 3. Za svaki blok napravi **desni klik → Ask Copilot** ili upiši prompt *"Copilot, odradi korake iz taska X"*.
>
> Po želji, nakon koraka **Bootstrap A** možeš sve checkbox‑e pretvoriti u GitHub Issues:  `gh issue import -F tasks.md --format markdown`.

---

## 🔰 Bootstrap A — lokalni setup (run once)

* [x] **Instaliraj alate**

  ```bash
  brew install gh pre-commit
  ```
* [x] **Ulogiraj se u GitHub CLI**

  ```bash
  gh auth login
  ```
* [x] **Pokreni pre-commit hook‑ove na cijelom repou**

  ```bash
  pre-commit run --all-files
  ```

---

## 1️⃣ Repo Clean‑Up & Konvencije

* [x] **Pronađi i ukloni sve `_old`, `_backup` i suvišne `.DS_Store` datoteke te dodaj ih u `.gitignore`**

> *Prompt Copilotu: **"Pronađi i ukloni sve *_old, *_backup i suvišne .DS_Store datoteke te dodaj ih u .gitignore"***

* [x] Obriši foldere/datoteke s sufiksima `_old`, `_backup`, `*-copy`.
* [x] Dodaj `*.orig`, `.DS_Store`, `__pycache__/` u **.gitignore** i `git rm -r --cached`.
* [x] **Detektiraj duplicirane migrations (`0001_initial.py`, `0002_auto_*`) → spoji ili izbriši**
* [x] **U `static/` i `templates/` zadrži samo stvarno korištene datoteke**.

## 2️⃣ Standardizacija naziva aplikacija

> *Prompt Copilotu: **"Preimenuj app 'client\_app' u 'client' i osvježi sve import‑e, settings i migracije."***

* [x] `client_app` → `client`
* [x] `projektiranje_app` → `projektiranje`
* [x] Ažuriraj `INSTALLED_APPS`, import putanje, `reverse()` pozive i testove.

## 3️⃣ Single Settings modul + Docker uniforma

* [x] Kreiraj `config/settings/` (base, dev, prod) + `settings/__init__.py`.
* [x] Podesi `django-environ` i `.env` predložak.
* [x] Napiši **docker-compose.dev.yml** (Postgres, Redis, Celery, web).
* [x] Dodaj VS Code/VS **.devcontainer/** (opcionalno).

## 4️⃣ Core & Multi‑Tenant Skeleton

* [x] Generiraj `core` app (tenants, org, permissions).
* [x] Premjesti `accounts` u `core.users` + custom User.
* [x] Tenant middleware (subdomain ili header).
* [x] Management command: `bootstrap_demo_tenant`.

## 5️⃣ Assets & Fixed Cost Engine

* [x] Dodaj modele: **Asset**, **AssetUsage**, **FixedCost**, **VariableCostPreset**.
* [x] Admin + import‑export CSV uplad.
* [x] Celery beat task: mjesečna amortizacija.

## 6️⃣ Project Costing & Profit‑Share

* [x] Modele: **Project**, **LabourEntry**, **MaterialUsage**, **CostLine**.
* [x] Signal: `Project.close` → break‑even + profit → **WorkerShare** kalkulacija.
* [x] Payout PDF report po radniku (WeasyPrint).

## 7️⃣ Benefits & Compliance

* [x] `benefits` app: Meal, Travel, Bonus + godišnji limiti.
* [x] Cron: dnevnice i topli obrok; provjera limita.
* [x] `compliance` app: ZNR, PZO, osiguranja + expiry reminders.

## 8️⃣ Dashboards (HTMX)

* [x] KPI board (projekti: zeleno/crveno vs break‑even).
* [x] Radnik dashboard: neoporezivi status + profit‑share.
* [x] QC checklist UI koja blokira start naloga bez ✅.

## 9️⃣ CI/CD & QA

* [ ] GitHub Actions: lint, mypy, pytest (coverage ≥ 85 %).
* [ ] Docker multistage build & push na registry.
* [ ] Auto‑deploy na staging (Dokku/Fly.io/ECS).

## 🔄 Sprint 0 — Definicija Dovršeno

* Repo nema `*_old` fajlova.
* Projekt se diže: `docker-compose up --build` → [http://localhost:8000](http://localhost:8000).
* `pytest` prolazi zeleno.
* Pre‑commit hook‑ovi prolaze bez errora.

---

## 📋 Brzi Copilot Promptovi (copy‑paste u chat)

```text
"Copilot, makni sve foldere s sufiksom _old i ažuriraj .gitignore."
"Copilot, napravi custom Django User unutar app-a core.users."
"Copilot, napiši signal koji na Project.close računa profit po WorkerShareu."
"Copilot, generiraj pytest case za Asset amortizacijski Celery task."
```

---

> **Savjet:** Kad task označiš ✅, commitaj mali patch (`git add -p`) i pushaj; Copilot 4o će lakše pratiti difove i sljedeće korake.
