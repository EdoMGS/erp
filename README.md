# ERP System

...

## Pre-commit hooks

Za automatsko formatiranje i lintanje koda koristi se pre-commit s hookovima (black, isort, flake8, djlint).

Pokreni:

```
pre-commit install
```

Za ručno pokretanje na svim datotekama:

```
pre-commit run --all-files
```

## Getting started (demo)

1. Create and activate a virtual environment, then install dependencies:
	 - Windows PowerShell:
		 - `python -m venv .venv`
		 - `.\.venv\Scripts\Activate.ps1`
		 - `pip install -r requirements.txt`
2. Run migrations: `python manage.py migrate`
3. Load minimal seed data: `python manage.py loaddata erp_system/fixtures/minimal.json`
4. Run tests: `python -m pytest -q`
5. Start server: `python manage.py runserver` and open API docs at `/docs/`.
