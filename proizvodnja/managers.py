from django.db import models
from django.utils import timezone


class RadniNalogManager(models.Manager):
    def get_active(self):
        return self.filter(is_active=True)

    def get_overdue(self):
        return self.filter(
            status__in=["OTVOREN", "U_TIJEKU"],
            datum_zavrsetka__lt=timezone.now().date(),
        )


class ProjektManager(models.Manager):
    def get_active_projects(self):
        return self.filter(is_active=True).exclude(status="ZAVRSENO")

    def get_projects_with_financials(self):
        return self.select_related("financial_details")
