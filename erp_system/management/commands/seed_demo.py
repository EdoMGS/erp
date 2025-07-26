from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from client.models import ClientSupplier
from financije.models.invoice import Invoice, InvoiceLine
from job_costing.models import JobCost
from tenants.models import Tenant


class Command(BaseCommand):
    help = "Seeds demo tenants, a sample job, and invoices."

    def handle(self, *args, **options):
        with transaction.atomic():
            # --- Tenants ---
            holding, _ = Tenant.objects.get_or_create(name="Holding")
            operativa, _ = Tenant.objects.get_or_create(name="Operativa")

            # --- Demo client for invoice ---
            client, _ = ClientSupplier.objects.get_or_create(
                name="Demo Klijent",
                defaults={
                    "address": "Demo Ulica 1",
                    "email": "demo@example.com",
                    "phone": "012345678",
                    "is_active": True,
                    "is_supplier": False,
                    "oib": "12345678901",
                    "country": "Hrvatska",
                    "city": "Zagreb",
                    "postal_code": "10000",
                },
            )

            # --- Sample Job ---
            job, _ = JobCost.objects.get_or_create(
                name="Sample Job",
                division="BRAVARIJA",
                defaults={
                    "cost_50": 500,
                    "owner_20": 200,
                    "workers_30": 300,
                    "total_cost": 1000,
                    "is_paid": False,
                },
            )

            # --- Sample Invoice ---
            invoice, _ = Invoice.objects.get_or_create(
                client=client,
                invoice_number="DEMO-001",
                defaults={
                    "issue_date": timezone.now().date(),
                    "due_date": timezone.now().date(),
                    "pdv_rate": 25.00,
                    "payment_method": "virman",
                    "status_fakture": "draft",
                    "paid": False,
                },
            )
            InvoiceLine.objects.get_or_create(
                invoice=invoice,
                description="Demo usluga",
                defaults={
                    "quantity": 1,
                    "unit_price": 1000,
                    "tax_rate": 25.00,
                },
            )

            self.stdout.write(self.style.SUCCESS("Demo tenants, job, and invoices created."))
