from decimal import Decimal

from .models import LocationConfig, RadnaEvaluacija


class PayrollCalculator:
    @staticmethod
    def compute(invoice_amount: Decimal, config: LocationConfig) -> dict:
        """
        Calculate payroll distribution based on invoice amount and location config.
        """
        worker_pool = invoice_amount * (config.worker_share / Decimal("100"))

        # Allocate minimal wage, employer contributions, meal, and housing allowances
        minimal_wage = config.gross_minimal + (config.gross_minimal * (config.employer_contrib_pct / Decimal("100")))
        allowances = config.meal_allowance_monthly + config.housing_allowance_monthly

        if worker_pool >= (minimal_wage + allowances):
            bonus_pool = worker_pool - (minimal_wage + allowances)
        else:
            bonus_pool = Decimal("0.00")

        return {
            "minimal_wage": minimal_wage.quantize(Decimal("0.01")),
            "allowances": allowances.quantize(Decimal("0.01")),
            "bonus_pool": bonus_pool.quantize(Decimal("0.01")),
        }


class EvaluacijaService:
    @staticmethod
    def kreiraj_evaluaciju(
        employee,
        evaluator,
        period,
        efikasnost,
        kvaliteta_rada,
        timski_rad,
        inicijativa,
        komentar,
    ):
        evaluacija = RadnaEvaluacija.objects.create(
            employee=employee,
            evaluator=evaluator,
            period=period,
            efikasnost=efikasnost,
            kvaliteta_rada=kvaliteta_rada,
            timski_rad=timski_rad,
            inicijativa=inicijativa,
            komentar=komentar,
        )
        return evaluacija
