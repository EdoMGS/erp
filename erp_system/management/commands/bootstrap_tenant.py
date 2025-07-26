from django.core.management.base import BaseCommand

from accounts.models import CustomUser
from client.models import ClientSupplier


class Command(BaseCommand):
    help = "Bootstrap a new tenant (Holding or Operativa) with initial data."

    def add_arguments(self, parser):
        parser.add_argument("name", type=str, help="Tenant name")
        parser.add_argument("--email", type=str, help="Admin email", default=None)

    def handle(self, *args, **options):
        name = options["name"]
        email = options["email"]
        # Example: create a ClientSupplier as tenant root
        tenant, created = ClientSupplier.objects.get_or_create(
            name=name,
            defaults={
                "email": email or f"{name.lower()}@example.com",
                "is_active": True,
            },
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Tenant "{name}" created.'))
        else:
            self.stdout.write(self.style.WARNING(f'Tenant "{name}" already exists.'))
        # Optionally, create an admin user for the tenant
        if email:
            user, user_created = CustomUser.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "is_staff": True,
                    "is_superuser": False,
                },
            )
            if user_created:
                self.stdout.write(self.style.SUCCESS(f'Admin user "{email}" created.'))
            else:
                self.stdout.write(self.style.WARNING(f'Admin user "{email}" already exists.'))
