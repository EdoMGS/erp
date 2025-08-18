from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Bonus, Evaluacija, Nagrada


@receiver(post_save, sender=Evaluacija)
def handle_evaluation(sender, instance, created, **kwargs):
    if created:
        last_3 = Evaluacija.objects.filter(employee=instance.employee).order_by("-datum_evaluacije")[:3]
        avg_score = sum(evaluacija.ocjena for evaluacija in last_3) / len(last_3)

        if avg_score >= 4.5:
            instance.employee.expertise_level = "senior"
            instance.employee.save()
            # Optionally, add a message or log
        elif avg_score <= 2.5:
            instance.employee.expertise_level = "junior"
            instance.employee.save()

        if instance.should_assign_bonus():
            Nagrada.objects.create(employee=instance.employee, amount=instance.bonus_amount)
            Bonus.objects.create(employee=instance.employee, amount=instance.bonus_amount)
            # Optionally, add a message or log
