# Stubbed Legacy Apps & Migration Simplification

This project has been pruned to a *minimal but functional* state to unblock new development.

## Overview
Several legacy domains (projektiranje_app, skladiste, proizvodnja) previously contributed a large, interdependent migration graph that prevented forward migrations in active apps (prodaja, financije, ljudski_resursi, common). Rather than fully restoring deprecated schemas, we introduced **stub models** and **collapsed / edited migrations** so historical ForeignKey / ManyToMany references no longer block `makemigrations` or `migrate`.

## What Was Done
- projektiranje_app reduced to a single model: `DesignTask` (stub) – all other models/forms/views/serializers removed.
- skladiste reduced to empty placeholder models: `Artikl`, `Zona`, `Materijal`, `Primka`.
- proizvodnja reduced to minimal placeholder models (`RadniNalog`, etc.) plus placeholder migrations 0002–0006 to satisfy downstream dependency chains.
- Removed or edited migrations in `financije`, `ljudski_resursi`, `prodaja`, and `common` that referenced deleted legacy models (e.g. `CADDocument`, `Primka`, `RadniNalog`, proposal drawing M2M, self‐FK content_object, audit trail change_type fields).
- Generated and patched merge migrations to reconcile divergent leaves, then iteratively stripped invalid RemoveField/AlterField operations that targeted already-pruned schema elements.

## Rationale
Reconstructing the full legacy schema would:
1. Reintroduce complexity with little current product value.
2. Increase maintenance and migration conflict surface.
3. Delay new feature work in active apps.

The stub strategy keeps historical FK targets satisfiable while treating removed concepts as inert placeholders.

## Implications
- Historical data tied to removed tables is not present (models dropped). Any required legacy data recovery would need a targeted extraction from old backups before reintroducing structure.
- New development should *not* add fields back into stub models inside the original collapsed migrations. Use **new forward migrations** instead.
- API endpoints for removed models have been removed; only `DesignTask` list + API viewset remains for projektiranje_app.

## Safe Extension Guidelines
1. When adding a new field to a stub model, create a fresh migration (do not edit the initial stub migration).
2. Avoid re-adding removed relations unless there is a concrete business requirement and you first audit downstream dependencies.
3. If a legacy field removal migration now no longer matches current state (because we pruned earlier), annotate it or convert to a no-op rather than deleting it retroactively.
4. Prefer referencing stub placeholders via simple CharFields (e.g. *_ref) instead of resurrecting deep cross-app FKs.

## Key Edited Migrations (Illustrative)
- projektiranje_app: 0001 kept minimal; 0002 & 0003 turned into no-ops; 0004 alters PK type only.
- prodaja: 0004 stripped `proposal_drawings` M2M; 0011 & 0013 skip FK alterations to removed/ external models.
- financije: 0003 removed `primka` FK; 0014 skipped primka ref replacement.
- ljudski_resursi: 0005 removed FK to proizvodnja.RadniNalog; 0010 unaffected after patch.
- common: 0003 & 0004 trimmed problematic self-referential and audit fields.

## Verification
`python manage.py migrate --settings=erp_system.settings.test --noinput` completes successfully (sqlite in-memory). This confirms graph consistency after pruning.

## Next Steps (Optional)
- Add a lightweight health check test ensuring migrations load (pytest invocation creating an empty test DB).
- Squash stub app migrations later (post-stabilization) to reduce noise.
- Introduce type hints and mypy config once models stabilize.

## Contact / Ownership
Document maintained as part of the migration stabilization effort (Aug 21 2025). Update if stub models evolve.
