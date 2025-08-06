from django.core.management import call_command, BaseCommand

# Fix blank lines per PEP8: two blank lines before class definitions


class Command(BaseCommand):
    help = "Wipes dev DB, runs all migrations and loads minimal fixture."

    def handle(self, *args, **kwargs):
        from django.conf import settings
        import os

        db_path = settings.DATABASES["default"]["NAME"]
        # Ensure no open connections lock the SQLite file
        from django.db import connections

        connections.close_all()
        if os.path.exists(db_path):
            os.remove(db_path)
            self.stdout.write(self.style.WARNING(f"💣  deleted {db_path}"))

        call_command("migrate", interactive=False)
        call_command("loaddata", "minimal")
        self.stdout.write(self.style.SUCCESS("✅  Fresh database ready"))
