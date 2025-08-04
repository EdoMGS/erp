## Zadaci za Copilot: Fix Docker PYTHONPATH

1. Update **Dockerfile**
   - WORKDIR `/code`
   - COPY `.` `/code`
   - ENV `PYTHONPATH="/code:${PYTHONPATH}"`

2. Update **docker-compose.yml**
   - Ukloni `working_dir`
   - Dodaj `DJANGO_SETTINGS_MODULE` varijable
   - Provjeri da svi servisi imaju isti `build` kontekst

3. Test:
   ```bash
docker compose build && \
  docker compose run --rm web python - <<'PY'
import sys
print('OK:', '/code' in sys.path)
PY
   ```

4. Commit message:
   ```bash
git commit -m "Fix PYTHONPATH in Docker setup"
```
