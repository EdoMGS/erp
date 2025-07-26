from django.core.management.base import BaseCommand, CommandError

from tenants.models import Tenant


class Command(BaseCommand):
    help = "Bootstrap a new tenant by name."

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, help="Name of the new tenant")
        parser.add_argument("domain", type=str, help="Domain of the new tenant")

    def handle(self, *args, **options):
        name = options["name"]
        domain = options["domain"]
        if Tenant.objects.filter(domain=domain).exists():
            raise CommandError(f"Tenant with domain '{domain}' already exists.")
        tenant = Tenant.objects.create(name=name, domain=domain)
        self.stdout.write(
            self.style.SUCCESS(f"Tenant '{tenant.name}' with domain '{tenant.domain}' created successfully.")
        )
