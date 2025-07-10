from django.db import models
from django.utils.translation import gettext_lazy as _
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone

class FinancialReports:
    @staticmethod
    def cash_flow_report(start_date, end_date):
        from financije.models.bank import CashFlow
        cash_flows = CashFlow.objects.filter(datum__range=[start_date, end_date])
        income = cash_flows.filter(tip_transakcije='priljev').aggregate(total=Sum('iznos'))['total'] or Decimal('0.00')
        expense = cash_flows.filter(tip_transakcije='odljev').aggregate(total=Sum('iznos'))['total'] or Decimal('0.00')
        return {
            "income": income,
            "expense": expense,
            "net_cash_flow": income - expense,
        }

    @staticmethod
    def profit_and_loss_report(year, month):
        from financije.models.invoice import Invoice
        from financije.models.overhead import Overhead
        income = Invoice.objects.filter(
            issue_date__year=year,
            issue_date__month=month
        ).aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
        expenses = Overhead.objects.filter(
            godina=year,
            mjesec=month
        ).aggregate(total=Sum('overhead_ukupno'))['total'] or Decimal('0.00')
        return {
            "income": income,
            "expenses": expenses,
            "profit": income - expenses,
        }

class BalanceSheet(models.Model):
    date = models.DateField(verbose_name=_("Datum"))
    assets = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    liabilities = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    equity = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))

    def __str__(self):
        return f"Balance Sheet as of {self.date}"

    class Meta:
        verbose_name = _("Balance Sheet")
        verbose_name_plural = _("Balance Sheets")

class FinancialReport(models.Model):
    PERIODS = [
        ('monthly', _("Monthly")),
        ('quarterly', _("Quarterly")),
        ('yearly', _("Yearly")),
    ]
    
    period = models.CharField(max_length=10, choices=PERIODS)
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField(null=True, blank=True)
    kvartal = models.PositiveIntegerField(null=True, blank=True)
    priljev_ukupno = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    odljev_ukupno = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    neto_cash_flow = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def generiraj_izvještaj(self):
        from financije.models.bank import CashFlow

        if self.period == 'monthly':
            priljev = CashFlow.objects.filter(
                tip_transakcije='priljev',
                datum__year=self.year,
                datum__month=self.month
            ).aggregate(ukupno=Sum('iznos'))['ukupno'] or Decimal('0.00')

            odljev = CashFlow.objects.filter(
                tip_transakcije='odljev',
                datum__year=self.year,
                datum__month=self.month
            ).aggregate(ukupno=Sum('iznos'))['ukupno'] or Decimal('0.00')

        elif self.period == 'quarterly':
            kvartal_mjeseci = {
                1: [1, 2, 3],
                2: [4, 5, 6],
                3: [7, 8, 9],
                4: [10, 11, 12]
            }
            mjeseci = kvartal_mjeseci.get(self.kvartal, [])
            
            priljev = CashFlow.objects.filter(
                tip_transakcije='priljev',
                datum__year=self.year,
                datum__month__in=mjeseci
            ).aggregate(ukupno=Sum('iznos'))['ukupno'] or Decimal('0.00')
            
            odljev = CashFlow.objects.filter(
                tip_transakcije='odljev',
                datum__year=self.year,
                datum__month__in=mjeseci
            ).aggregate(ukupno=Sum('iznos'))['ukupno'] or Decimal('0.00')
        
        else:  # yearly
            priljev = CashFlow.objects.filter(
                tip_transakcije='priljev',
                datum__year=self.year
            ).aggregate(ukupno=Sum('iznos'))['ukupno'] or Decimal('0.00')
            
            odljev = CashFlow.objects.filter(
                tip_transakcije='odljev',
                datum__year=self.year
            ).aggregate(ukupno=Sum('iznos'))['ukupno'] or Decimal('0.00')

        self.priljev_ukupno = priljev
        self.odljev_ukupno = odljev
        self.neto_cash_flow = priljev - odljev
        self.save()

    def __str__(self):
        return f"{self.get_period_display()} Report - {self.year}"

    class Meta:
        verbose_name = _("Financijski izvještaj")
        verbose_name_plural = _("Financijski izvještaji")
