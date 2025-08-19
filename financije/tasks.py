# financije/tasks.py

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.utils import timezone

from financije.models.break_even import BreakEvenSnapshot
from financije.models.fixed_costs import FixedCost
from tenants.models import Tenant


@shared_task(name='financije.tasks.snapshot_break_even')
def snapshot_break_even():
    today = timezone.now().date()
    channel_layer = get_channel_layer()

    for tenant in Tenant.objects.all():
        for division in FixedCost.objects.filter(tenant=tenant).values_list("division", flat=True).distinct():
            fixed_sum = sum(fc.monthly_value() for fc in FixedCost.objects.filter(tenant=tenant, division=division))

            BreakEvenSnapshot.objects.create(
                tenant=tenant,
                division=division,
                date=today,
                fixed_costs=fixed_sum,
                # Ostala polja: revenue, profit, break_even_qty, status...
            )

        # Trigger WebSocket update
        async_to_sync(channel_layer.group_send)(
            f"break_even_{tenant.pk}",
            {"type": "break_even_update"},
        )

    # Confirmation log for Celery Beat
    print("snapshot created")


@shared_task(name='financije.tasks.create_interco_invoice')
def create_interco_invoice():
    """Generate invoices for invoiceable asset usage records."""
    from asset_usage.models import AssetUsage

    from financije.models.invoice import Invoice, InvoiceLine

    usages = AssetUsage.objects.filter(invoiceable=True, is_deleted=False)
    for usage in usages:
        # Create Invoice
        invoice = Invoice.objects.create(
            client=usage.client,
            issue_date=usage.usage_date,
            due_date=usage.usage_date,
            payment_method='virman',
            status_fakture='draft',
        )
        # Add a line item for the usage amount
        InvoiceLine.objects.create(
            invoice=invoice,
            description=str(usage),
            quantity=1,
            unit_price=usage.amount,
        )
        # Mark usage as invoiced
        usage.invoiceable = False
        usage.save()


@shared_task(name='financije.tasks.generate_worker_payouts')
def generate_worker_payouts(invoice_id):
    """
    Stub task: generate worker payouts for a paid invoice.
    """
    from financije.models.invoice import Invoice

    try:
        invoice = Invoice.objects.get(pk=invoice_id)
        # TODO: implement payout distribution logic
        print(f"Generating worker payouts for Invoice {invoice.invoice_number}")
    except Invoice.DoesNotExist:
        print(f"Invoice {invoice_id} not found for payout generation")
