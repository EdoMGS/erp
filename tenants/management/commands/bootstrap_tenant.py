from django.core.management import call_command
from django.core.management.base import BaseCommand

from tenants.models import Tenant


class Command(BaseCommand):
    help = 'Bootstrap a tenant with demo data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--demo',
            action='store_true',
            help='Create demo tenant and load demo fixtures.',
        )

    def handle(self, *args, **options):
        if options.get('demo'):
            tenant, created = Tenant.objects.get_or_create(domain='demo', defaults={'name': 'Demo Tenant'})
            status = 'created' if created else 'exists'
            self.stdout.write(self.style.SUCCESS(f'Tenant "{tenant}" {status}.'))

            # Load demo fixtures
            fixtures = [
                'initial_fixed_costs',
                'initial_variable_costs',
                'paint_price',
            ]
            for fixture in fixtures:
                call_command('loaddata', fixture)
                self.stdout.write(self.style.SUCCESS(f'Loaded fixture "{fixture}"'))
        else:
            self.stdout.write(self.style.WARNING('No action taken. Use --demo flag.'))
