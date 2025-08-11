from django.core.management.base import BaseCommand

from core.models import Tenant  # Assuming a Tenant model exists


class Command(BaseCommand):
    help = "Bootstrap a demo tenant"

    def handle(self, *args, **kwargs):
        tenant, created = Tenant.objects.get_or_create(
            name="Demo Tenant",
            defaults={
                "domain": "demo.example.com",
                "schema_name": "demo",
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS("Successfully created demo tenant."))
        else:
            self.stdout.write(self.style.WARNING("Demo tenant already exists."))
