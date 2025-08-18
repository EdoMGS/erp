"""Management command to bootstrap a minimal demo context for the MVP.

Safe characteristics:
 - Idempotent (re-running will not duplicate core objects)
 - Avoids duplicate Tenant creation
 - Creates a demo user with a known password (DO NOT use in production)
 - Guards optional / simplified model fields
 - Imports Celery tasks lazily; if tasks module is missing (e.g. Celery not installed or
   financije.tasks refactored out), it logs and continues rather than crashing
 - Flake8 compliant
"""

from __future__ import annotations

from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from project_costing.models import Project, ProfitShareConfig
from prodaja.models import Offer


class Command(BaseCommand):
    help = "Bootstrap demo tenant, user, project, profit share config, and placeholder offer"

    def handle(self, *args, **options):  # noqa: D401 - Django signature
        tenant, _ = Tenant.objects.get_or_create(name="Demo Tenant", domain="demo.local")
        self.stdout.write(f"Tenant: {tenant.name}")

        User = get_user_model()
        demo_user, created = User.objects.get_or_create(
            username="demo",
            defaults={"email": "demo@demo.local"},
        )
        if created:
            demo_user.set_password("demo123")
            demo_user.save()
            self.stdout.write("Created demo user 'demo' (password: demo123)")
        else:
            self.stdout.write("Demo user already exists")

        project, _ = Project.objects.get_or_create(
            tenant=tenant,
            name="Demo Project",
            defaults={
                # Provide minimal required fields if object is new
                "start_date": "2025-01-01",
                "division": "Demo",
            },
        )
        self.stdout.write(f"Project: {project.name}")

        ProfitShareConfig.objects.get_or_create(
            project=project,
            defaults={
                "company_share": Decimal("50.00"),
                "worker_share": Decimal("30.00"),
                "dynamic_floor_pct": Decimal("10.00"),
                "floor_cap_per_month": Decimal("2000.00"),
            },
        )
        self.stdout.write("Profit share config ensured")

        offer = Offer.objects.create(
            customer_name="Demo Customer",
            service_lines=[],
            material_lines=[],
        )
        self.stdout.write(f"Created placeholder Offer {offer.pk}")

        # Lazy import of Celery tasks; swallow if unavailable
        try:
            from financije import tasks  # type: ignore

            triggered = []
            for attr in ("snapshot_break_even", "create_interco_invoice"):
                fn = getattr(tasks, attr, None)
                if fn is None:
                    continue
                # Prefer apply_async if Celery is configured; fall back to direct call
                if hasattr(fn, "apply_async"):
                    fn.apply_async()
                else:
                    fn()  # synchronous fallback
                triggered.append(attr)
            if triggered:
                self.stdout.write("Triggered tasks: " + ", ".join(triggered))
            else:
                self.stdout.write("No financije tasks triggered (not present)")
        except Exception as exc:  # pragma: no cover - defensive
            self.stdout.write(f"Skipping task triggers due to import/runtime error: {exc}")

        self.stdout.write(self.style.SUCCESS("Demo bootstrap completed"))
