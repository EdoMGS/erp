from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.utils import timezone

from financije.models import BreakEvenSnapshot
from financije.models.fixed_costs import FixedCost
from tenants.models import Tenant


@shared_task
def write_break_even_snapshots():
    today = timezone.now().date()
    channel_layer = get_channel_layer()
    for tenant in Tenant.objects.all():
        for division in FixedCost.objects.filter(tenant=tenant).values_list("division", flat=True).distinct():
            fixed_sum = sum(fc.monthly_value() for fc in FixedCost.objects.filter(tenant=tenant, division=division))
            snapshot = BreakEvenSnapshot.objects.create(
                tenant=tenant,
                division=division,
                date=today,
                fixed_costs=fixed_sum,
                # Ostala polja: revenue, profit, break_even_qty, status...
            )
        # Trigger WebSocket update
        async_to_sync(channel_layer.group_send)(f"break_even_{tenant.pk}", {"type": "break_even_update"})
