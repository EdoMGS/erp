## Development Workflow

### Fast Local Loop
1. Create/activate local venv
2. Install deps: `pip install -r requirements.txt`
3. Run tests quickly (SQLite): `make test-fast`
4. Add / adjust tests + code

### Full Suite / Coverage
`make test-all` produces coverage summary (extend later with htmlcov).

### Docker Validation
Used before pushing larger changes or when integrating services (Postgres, Redis, Celery workers).

```
docker-compose up -d --build
make test-docker
```

Current dev settings (`project_root/settings/dev.py`) still point to SQLite even inside the container; switch to Postgres by uncommenting the provided block when ready and setting env vars (already present: `DATABASE_URL`).

### Factories
Lightweight manual factories live in `tests/factories.py`. Prefer reusing them instead of ad‑hoc object creation inside tests. If complexity grows, introduce `factory_boy`.

### Adding Tests
Place new test modules under the app's `tests/` package or top-level `tests/`. Use `pytest.mark.django_db` where DB access is required.

### Pre-commit
Run `make lint` (executes pre-commit hooks on all files). Configure additional hooks in `.pre-commit-config.yaml`.

### Next Improvements (Backlog)
- Integrate Postgres in dev (switch DATABASES in `dev.py`).
- Introduce HTML coverage report target (`make coverage-html`).
- Implement profit share engine when branch is available.
- Gradually restore stricter model constraints once fixtures/factories cover required data.

### Celery
Currently broker configured as in-memory for dev/tests. Docker compose defines Redis + workers; to use Redis broker set `CELERY_BROKER_URL=redis://redis:6379/0` and update settings.

---
This document will evolve as the architecture stabilizes.
