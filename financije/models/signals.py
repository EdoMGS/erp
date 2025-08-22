from decimal import Decimal

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from financije.ledger import post_transaction
from financije.models.audit import AuditLog  # use central AuditLog
from financije.models.invoice import Invoice


def create_audit_log(user, action, model_name, instance_id):
    AuditLog.objects.create(
        user=user, action=action, model_name=model_name, instance_id=instance_id
    )


@receiver(post_save, sender=Invoice)
def log_invoice_save(sender, instance, created, **kwargs):
    if instance.user:
        action = "Created Invoice" if created else "Updated Invoice"
        create_audit_log(instance.user, action, "Invoice", instance.pk)


@receiver(post_delete, sender=Invoice)
def log_invoice_delete(sender, instance, **kwargs):
    if instance.user:
        create_audit_log(instance.user, "Deleted Invoice", "Invoice", instance.id)


@receiver(post_save, sender=Invoice)
def auto_journalize_invoice(sender, instance, created, **kwargs):
    """On approved invoice, post to ledger via central engine.

    Uses event SALE_INVOICE_POSTED with payload of net and VAT. Idempotent by key.
    """
    if instance.status_fakture == "odobreno":
        with transaction.atomic():
            payload = {
                "issue_date": instance.issue_date,
                "description": f"Automatsko knjiženje računa br. {instance.invoice_number}",
                "net": Decimal(instance.amount),
                "vat": Decimal(instance.pdv_amount),
            }
            idem_key = f"{getattr(instance, 'tenant_id', 'na')}:invoice:{instance.pk}:posted"
            post_transaction(
                tenant=getattr(instance, "tenant", None),
                event="SALE_INVOICE_POSTED",
                payload=payload,
                idempotency_key=idem_key,
                lock=True,
            )
