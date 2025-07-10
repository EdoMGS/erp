# nalozi/management/commands/fetch_tax_data.py

from django.core.management.base import BaseCommand
from nalozi.utils import fetch_tax_data


class Command(BaseCommand):
    help = 'Dohvaća i ažurira podatke o porezima, doprinosima i općinama'

    def handle(self, *args, **options):
        fetch_tax_data()
        self.stdout.write(self.style.SUCCESS('Podaci su uspješno ažurirani.'))
