# 🚀  ERP Sprint 0 — Core Skeleton, Break‑Even MVP & CI 🟢

> **Cilj:** u < 5 dana dignuti reproducibilni dev stack
> (Docker + Celery + PostgreSQL), imati *zeleni* GitHub Actions,
> dnevni `BreakEvenSnapshot` i dashboard koji pokazuje crveno ↔ žuto ↔ zeleno.

---

## 0 . Preduvjeti (lokalni stroj)

| Što | Verzija / min |
|-----|---------------|
| Docker Desktop | 4 .27 + |
| docker‑compose | v2 |
| Git | 2.40 + |
| Node /npm (samo za Tailwind) | 20 / 10 |
| VS Code + Copilot | aktualni |
| SSH ključ na GH | ✔ |

---

## 1 . Repo & grana

1. `git clone git@github.com:EdoMGS/erp.git`
2. `git switch -c feature/sprint0-skeleton`

✅  *`git status` čist; nova grana spremna za push.*

---

## 2 . Python deps + pre‑commit

```bash
python -m venv .venv

# Linux/macOS:
. .venv/bin/activate

# Windows PowerShell:
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
pre-commit install
pre-commit run --all-files   # mora proći bez errora

3 . .env.dev (copy → paste)

# Django
DEBUG=1
SECRET_KEY=devsecretkey123
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# DB
POSTGRES_DB=erp
POSTGRES_USER=erp
POSTGRES_PASSWORD=erp
POSTGRES_HOST=db
POSTGRES_PORT=5432
#  alternativa: DATABASE_URL=postgres://erp:erp@db:5432/erp

# Redis
REDIS_URL=redis://redis:6379/0

    NB: docker-compose.yml mora imati
    env_file: - .env.dev za web / worker / beat servise.

✅ .env.dev postoji; docker compose config pokazuje varijable.
4 . Docker stack ↑

docker compose up -d --build

✅ docker compose ps → svi servisi Up (web ne restart‑loopa).
✅ curl -I localhost:8000 → 200 OK ili 302 Found.
5 . Init DB & tenant demo

docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py bootstrap_tenant --demo
docker compose exec web python manage.py loaddata \
    initial_fixed_costs initial_variable_costs paint_price

✅ login u /admin radi sa superuserom.
6 . FixedCost & BreakEven početni podaci

    Konstante dogovorene u chatu.

# 1 × shell‑one‑liner
from financije.models import FixedCost, BreakEvenRule
from datetime import date, timedelta

FixedCost.objects.bulk_create([
    FixedCost(division='General', name='Najam hale',   amount=1800, period='M'),
    FixedCost(division='General', name='Struja+Voda',  amount=1000, period='M'),
    FixedCost(division='General', name='Leasing auto', amount=500,  period='M'),
    FixedCost(division='General', name='Gorivo',       amount=500,  period='M'),
])

BreakEvenRule.objects.create(
    start_date=date.today(),
    end_date=date.today()+timedelta(days=90),
    current_split="40/40/20",
    fixed_cost=5460,
    baseline_pool=6930,   # (3 radnika × 1500  + direktor minimalac)
)

✅ /admin/financije/breakevenrule/ prikazuje zapis.
7 . Celery Beat ‑ dnevni BreakEvenSnapshot

    Lokacija zadatka: financije.tasks.snapshot_break_even

    Periodic task: every day 00:05 UTC

    Upisuje date, target_revenue, current_revenue,
    status (red / yellow / green)

✅ docker compose logs beat pokazuje “snapshot created”.
8 . Dashboard MVP
URL	Komponenta	Definition of Done
/dashboard/break-even	HTMX partial	prikazuje progress‑bar:  <50 % = 🔴, 50‑99 % = 🟡, ≥ 100 % = 🟢
/dashboard/	full page	embed HTMX + link na ostale KPI‑e

CSS: Tailwind + bg-red-500 / bg-yellow-400 / bg-green-500

✅ manualni refresh nakon unosa fixture pokazuje crvenu traku.
9 . Testovi

pytest -m smoke          # quick
pytest                   # full suite
coverage run -m pytest && coverage html

Dodaj nove file‑ove:

financije/tests/test_break_even.py          # model + snapshot
dashboard/tests/test_break_even_view.py     # 200 OK + correct colour

✅ 100 % pass lokalno i u GitHub Actions.
10 . CI / GitHub Actions

    Workflow: .github/workflows/ci.yml

    Job matrix: py 3.10 / 3.11, OS ubuntu‑latest

    Steps: checkout → setup‑python → pip install -r requirements.txt
    → pre‑commit → pytest -m smoke (fast)
    – “full” test job može se pokretati nightly.

Badge za README:

![CI](https://github.com/EdoMGS/erp/actions/workflows/ci.yml/badge.svg)

✅ badge zelen na main.