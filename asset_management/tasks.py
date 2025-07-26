from datetime import date
from decimal import Decimal

from celery import shared_task

from .models import Asset


@shared_task
def calculate_monthly_amortization():
    today = date.today()
    assets = Asset.objects.all()
    for asset in assets:
        # Example amortization logic: reduce value by 1% monthly
        asset.value *= Decimal("0.99")
        asset.save()
    return f"Amortization calculated for {len(assets)} assets on {today}"
