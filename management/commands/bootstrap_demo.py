from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from tenants.models import Tenant
from project_costing.models import Project, ProfitShareConfig
from prodaja.models import Offer
from proizvodnja.models import Projekt, RadniNalog
from financije.models.invoice import Invoice
from financije.tasks import snapshot_break_even, create_interco_invoice, generate_worker_payouts


class Command(BaseCommand):
    help = 'Bootstrap demo tenant, users, rates, and demo workflow'

    def handle(self, *args, **options):
        # Create demo tenant and user
        tenant, _ = Tenant.objects.get_or_create(name='Demo Tenant', domain='demo.local')
        User = get_user_model()
        demo_user, created = User.objects.get_or_create(username='demo', defaults={'email': 'demo@demo.local'})
        if created:
            demo_user.set_password('demo123')
            demo_user.save()
        self.stdout.write('Created demo tenant and user')

        # Create project and profit share config
        project, _ = Project.objects.get_or_create(
            tenant=tenant,
            name='Demo Project',
            start_date='2025-01-01',
            division='Demo'
        )
        config, _ = ProfitShareConfig.objects.get_or_create(
            project=project,
            defaults={
                'company_share': 50.00,
                'worker_share': 30.00,
                'dynamic_floor_pct': 0.10,
                'floor_cap_per_month': 2000.00,
            }
        )
        self.stdout.write('Configured profit share')

        # Create an Offer and approve it, generating WorkOrder
        offer = Offer.objects.create(customer=tenant.clientsupplier_set.first(), service_lines=[], material_lines=[])
        self.stdout.write(f'Created Offer {offer.pk}')
        # Normally you'd call offer.approve(), here stub:
        self.stdout.write('Approve and create WorkOrder not implemented in demo')

        # Trigger snapshot and invoice creation
        snapshot_break_even.delay()
        create_interco_invoice.delay()
        self.stdout.write('Triggered Celery tasks for snapshot and invoice creation')

        # Simulate marking invoice as paid and payout
        self.stdout.write('Demo bootstrap completed')
