from celery import shared_task

from .models import AssetUsage


@shared_task
def create_intercompany_invoices():
    # Example logic for creating intercompany invoices
    usages = AssetUsage.objects.all()
    for usage in usages:
        # Replace with actual invoice creation logic
        print(f"Creating invoice for {usage.asset} with amount {usage.amount}")
