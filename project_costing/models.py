# project_costing/models.py

from decimal import Decimal
from django.db import models
from tenants.models import Tenant


class Project(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    name = models.CharField(max_length=128)
    start_date = models.DateField()
    division = models.CharField(max_length=64)


class ProfitShareConfig(models.Model):
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name="profit_share_config",
    )
    company_share = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("50.00")
    )
    worker_share = models.DecimalField(
        max_digits=5, decimal_places=2, default=Decimal("30.00")
    )
    dynamic_floor_pct = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal("10.00")
    )
    floor_cap_per_month = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("2000.00")
    )
    ramp_up_company_pct = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal("40.00")
    )
    ramp_up_worker_pct = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal("40.00")
    )
    ramp_up_fund_pct = models.DecimalField(
        max_digits=4, decimal_places=2, default=Decimal("20.00")
    )

    def calculate_shares(self, invoice_amount: Decimal, is_ramp_up: bool) -> dict:
        """
        Returns dict with keys: floor, company_after_floor, fund, worker
        """
        # 1) compute floor (owner reserve)
        floor_pct = self.dynamic_floor_pct / Decimal("100")
        floor = min(invoice_amount * floor_pct, self.floor_cap_per_month)
        remainder = invoice_amount - floor

        # 2) compute worker and fund
        if is_ramp_up:
            worker = remainder * (self.worker_share / Decimal("100")) * Decimal("0.5")
            fund = worker
        else:
            worker = remainder * (self.worker_share / Decimal("100"))
            fund = Decimal("0.00")

        # 3) company gets the rest
        company_after_floor = remainder - (worker + fund)

        # 4) round to cents
        return {
            "floor": floor.quantize(Decimal("0.01")),
            "company_after_floor": company_after_floor.quantize(Decimal("0.01")),
            "fund": fund.quantize(Decimal("0.01")),
            "worker": worker.quantize(Decimal("0.01")),
        }
