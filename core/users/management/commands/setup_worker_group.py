from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Create or update the read-only "worker" group with appropriate permissions.'

    def handle(self, *args, **options):
        group, created = Group.objects.get_or_create(name="worker")
        # Remove all permissions first
        group.permissions.clear()
        # Add only view permissions for all models
        for perm in Permission.objects.filter(codename__startswith="view_"):
            group.permissions.add(perm)
        self.stdout.write(
            self.style.SUCCESS('Group "worker" created/updated with read-only permissions.')
        )
