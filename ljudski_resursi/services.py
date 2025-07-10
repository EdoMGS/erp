from .models import RadnaEvaluacija

class EvaluacijaService:
    @staticmethod
    def kreiraj_evaluaciju(employee, evaluator, period, efikasnost, kvaliteta_rada, timski_rad, inicijativa, komentar):
        evaluacija = RadnaEvaluacija.objects.create(
            employee=employee,
            evaluator=evaluator,
            period=period,
            efikasnost=efikasnost,
            kvaliteta_rada=kvaliteta_rada,
            timski_rad=timski_rad,
            inicijativa=inicijativa,
            komentar=komentar
        )
        return evaluacija
