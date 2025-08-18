from celery import shared_task
from django.utils.timezone import now

from .models import AssetUsage


@shared_task
def create_monthly_rent_invoices():
    for usage in AssetUsage.objects.filter(invoiceable=True, is_deleted=False):
        # Ovdje ide logika za generiranje fakture
        print(f"Kreiram fakturu za: {usage.content_object} ({now()})")
