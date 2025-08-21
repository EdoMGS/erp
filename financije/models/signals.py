from decimal import Decimal

from django.db import transaction
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from financije.models.accounting import Account, JournalEntry, JournalItem
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
    if instance.status_fakture == "odobreno":
        with transaction.atomic():
            # Create journal entry
            journal_entry = JournalEntry.objects.create(
                date=instance.issue_date,
                description=f"Automatsko knjiženje računa br. {instance.invoice_number}",
                user=instance.user,
            )

            # Get accounts (make sure these account numbers exist)
            kupci_konto = Account.objects.get(number="1200")  # Kupci
            prihodi_konto = Account.objects.get(number="4000")  # Prihodi
            pdv_konto = Account.objects.get(number="4700")  # PDV obveze

            # Calculate amounts
            pdv_iznos = instance.pdv_amount
            osnovica = instance.amount

            # Create journal items
            JournalItem.objects.create(
                entry=journal_entry,
                account=kupci_konto,
                debit=osnovica + pdv_iznos,
                credit=Decimal("0.00"),
            )

            JournalItem.objects.create(
                entry=journal_entry,
                account=prihodi_konto,
                debit=Decimal("0.00"),
                credit=osnovica,
            )

            JournalItem.objects.create(
                entry=journal_entry,
                account=pdv_konto,
                debit=Decimal("0.00"),
                credit=pdv_iznos,
            )
