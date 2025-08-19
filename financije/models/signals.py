from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from prodaja.models import Invoice


@receiver(post_save, sender=Invoice)
def log_invoice_save(sender, instance, created, **kwargs):  # pragma: no cover
    pass


@receiver(post_delete, sender=Invoice)
def log_invoice_delete(sender, instance, **kwargs):  # pragma: no cover
    pass


@receiver(post_save, sender=Invoice)
def auto_journalize_invoice(sender, instance, created, **kwargs):  # pragma: no cover
    pass
