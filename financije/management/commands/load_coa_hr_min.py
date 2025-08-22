from django.core.management.base import BaseCommand

from financije.models import Account

MIN_COA = [
    ("110", "Banka", "active"),
    ("120", "Kupci (AR)", "active"),
    ("200", "Obveze", "passive"),
    ("220", "Dobavljači (AP)", "passive"),
    ("270", "Primljeni avansi", "passive"),
    ("400", "Prihodi od prodaje", "income"),
    ("460", "Prihodi intercompany", "income"),
    ("470", "PDV obveza", "passive"),
    ("471", "PDV pretporez", "active"),
    ("500", "Materijal i usluge", "expense"),
    ("560", "Trošak intercompany", "expense"),
    ("600", "Bruto plaće", "expense"),
    ("610", "Doprinosi", "expense"),
    ("630", "Profit share pool 30%", "expense"),
    ("700", "Amortizacija", "expense"),
]


class Command(BaseCommand):
    help = "Load a minimal HR/EU Chart of Accounts"

    def add_arguments(self, parser):
        parser.add_argument("tenant_id", type=int, help="Tenant ID to load accounts into")

    def handle(self, *args, **options):
        tenant_id = options["tenant_id"]
        created = 0
        for number, name, kind in MIN_COA:
            obj, was_created = Account.objects.get_or_create(
                tenant_id=tenant_id,
                number=number,
                defaults={"name": name, "account_type": kind},
            )
            created += 1 if was_created else 0
        self.stdout.write(self.style.SUCCESS(f"COA loaded/ensured. New created: {created}"))
