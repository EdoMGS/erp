from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.management.base import BaseCommand

from job_costing.models import JobCost


class Command(BaseCommand):
    help = "Push dashboard update to websocket clients."

    def handle(self, *args, **kwargs):
        qs = JobCost.objects.all()
        data = [
            {
                "id": jc.id,
                "name": jc.name,
                "revenue": float(jc.total_cost),
                "cost_50": float(jc.cost_50),
                "owner_20": float(jc.owner_20),
                "workers_30": float(jc.workers_30),
                "kpi_status": "OK" if jc.is_paid else "PENDING",
            }
            for jc in qs
        ]
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "dashboard", {"type": "dashboard_update", "data": {"rows": data}}
        )
        self.stdout.write(self.style.SUCCESS("Dashboard update pushed."))
