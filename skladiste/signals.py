from django.db.models.signals import post_save  # post_delete unused, removed
from django.dispatch import receiver

from financije.models import FinancijskaTransakcija

from .models import Artikl, Materijal


@receiver(post_save, sender=Artikl)
def update_financije_artikl(sender, instance, created, **kwargs):
    """Ažurira financijske podatke kad se promijeni stanje artikla"""
    if not created:
        FinancijskaTransakcija.objects.create(
            iznos=instance.get_total_value(),
            opis=f"Promjena stanja artikla {instance.naziv}",
            content_object=instance,
        )


@receiver(post_save, sender=Materijal)
def update_financije_materijal(sender, instance, created, **kwargs):
    """Ažurira financijske podatke kad se promijeni materijal"""
    if not created and instance.artikl:
        FinancijskaTransakcija.objects.create(
            iznos=instance.artikl.get_total_value(),
            opis=f"Promjena materijala {instance.naziv}",
            content_object=instance,
        )


# ...more signals...
