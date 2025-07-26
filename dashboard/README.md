# Dashboard App (HTMX + Channels)

## Opis
ERP dashboard prikazuje real-time tablicu s ključnim KPI podacima:
- revenue
- cost_50
- owner_20
- workers_30
- KPI status

Podaci se ažuriraju websocketom (Django Channels) i htmx-om.

## Sastavni dijelovi
- `dashboard/views.py`: Django view za prikaz i API endpoint za podatke
- `dashboard/consumers.py`: Channels websocket consumer za push ažuriranja
- `dashboard/templates/dashboard/dashboard.html`: HTMX + JS frontend
- `dashboard/urls.py`: URL konfiguracija
- `dashboard/routing.py`: Channels routing
- `dashboard/management/commands/push_dashboard_update.py`: Management command za push
- `erp_system/routing.py`: Channels root routing

## Pokretanje
1. Dodaj `dashboard` u `INSTALLED_APPS`.
2. U `urls.py` dodaj `path('dashboard/', include('dashboard.urls'))`.
3. U `routing.py` dodaj websocket routing.
4. Pokreni ASGI server (`daphne` ili `python manage.py runserver` s Channels).
5. Otvori `/dashboard/` u browseru.
6. Za test push koristi: `python manage.py push_dashboard_update`

## Ovisnosti
- Django Channels
- htmx.js
- reconnecting-websocket.js

## Napomena
- Dashboard prikazuje podatke iz modela `JobCost`.
- Svaka promjena može se pushati websocketom za instant refresh tablice.
