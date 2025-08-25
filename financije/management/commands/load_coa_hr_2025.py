from django.core.management.base import BaseCommand

from financije.models import Account
from financije.services import load_coa_hr_2025
from tenants.models import Tenant


class Command(BaseCommand):
    help = "Load the full Croatian chart of accounts for 2025"

    def add_arguments(self, parser):
        parser.add_argument("tenant_id", type=int, help="Tenant ID to load accounts into")

    def handle(self, *args, **options):
        tenant = Tenant.objects.get(pk=options["tenant_id"])
        before = Account.objects.filter(tenant=tenant).count()
        load_coa_hr_2025(tenant)
        after = Account.objects.filter(tenant=tenant).count()
        self.stdout.write(self.style.SUCCESS(f"COA loaded/ensured. New created: {after - before}"))
