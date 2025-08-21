from decimal import Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import FondRadnici


@receiver(post_save, sender=FondRadnici)
def update_job_cost_fields(sender, instance, **kwargs):
    job_cost = instance.job_cost
    fond = job_cost.fond_radnici.all()
    sum(fr.hours for fr in fond if fr.quality_ok)
    total_fond = job_cost.workers_30
    # Ulogu ponderiramo: mentor x1.2, majstor x1.0, pomoćni x0.7
    role_weights = {
        "mentor": Decimal("1.2"),
        "majstor": Decimal("1.0"),
        "pomocni": Decimal("0.7"),
    }
    total_weight = sum(
        fr.hours * role_weights.get(fr.role, Decimal("1.0")) for fr in fond if fr.quality_ok
    )
    # Raspodjela fonda po ponderu, uz bonus i penal
    for fr in fond:
        if not fr.quality_ok:
            fr.bonus = Decimal("0.00")
            fr.penalty = fr.penalty or Decimal("0.00") + (total_fond / len(fond))  # penalizacija
            continue
        share = (
            (fr.hours * role_weights.get(fr.role, Decimal("1.0"))) / total_weight
            if total_weight
            else Decimal("0.00")
        )
        (total_fond * share) + fr.bonus - fr.penalty
        # Ovdje bi se moglo spremiti bruto izračun po radniku (npr. fr.bruto = bruto)
        # fr.save(update_fields=["bonus", "penalty", "bruto"])
    # Ažuriraj ukupne troškove
    job_cost.cost_50 = job_cost.total_cost * Decimal("0.5")
    job_cost.owner_20 = job_cost.total_cost * Decimal("0.2")
    job_cost.workers_30 = job_cost.total_cost * Decimal("0.3")
    job_cost.save()
