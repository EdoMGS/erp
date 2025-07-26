from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import LabourEntry, ProfitShareConfig, Project, WorkerShare


@receiver(post_save, sender=Project)
def allocate_profit_share(sender, instance, created, **kwargs):
    if not created:
        return
    # Pretpostavka: profit = revenue - sum(cost_lines.amount)
    total_cost = sum(cl.amount for cl in instance.cost_lines.all())
    gross_profit = instance.revenue - total_cost
    if gross_profit > 0:
        config = getattr(instance, "profit_share_config", None)
        if not config:
            config = ProfitShareConfig.objects.create(project=instance)
        gross_profit * config.owner_share / Decimal("100.00")
        worker_amount = gross_profit * config.worker_share / Decimal("100.00")
        # Pretpostavka: svi radnici iz LabourEntry dijele worker_amount
        workers = set(le.worker for le in instance.labour_entries.all())
        per_worker = worker_amount / len(workers) if workers else Decimal("0.00")
        for worker in workers:
            WorkerShare.objects.create(project=instance, worker=worker, amount=per_worker)
    # Ako profit <= 0, ne radi se raspodjela


@receiver(post_save, sender=Project)
def calculate_profit_on_close(sender, instance, **kwargs):
    if instance.end_date:  # Assuming end_date indicates project closure
        total_labour_cost = sum(
            entry.hours_worked * entry.hourly_rate for entry in LabourEntry.objects.filter(project=instance)
        )
        profit = instance.budget - total_labour_cost
        # Example logic: distribute profit equally among workers
        workers = LabourEntry.objects.filter(project=instance).values_list("worker_name", flat=True).distinct()
        worker_share = profit / Decimal(len(workers)) if workers else Decimal("0.00")
        print(f"Profit per worker: {worker_share}")
