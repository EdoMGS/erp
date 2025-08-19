from django.db import models
from django.utils.translation import gettext_lazy as _

from prodaja.models import Invoice, InvoiceLine


class Payment(models.Model):
    related_invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="payments")
    created_at = models.DateTimeField(auto_now_add=True)


class Debt(models.Model):
    client_name = models.CharField(max_length=255, verbose_name=_("Client"))
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="debts", verbose_name=_("Invoice"))
    due_date = models.DateField(verbose_name=_("Due Date"))
    amount_due = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Amount Due"))
    is_paid = models.BooleanField(default=False, verbose_name=_("Is Paid"))

    def days_overdue(self):
        if not self.is_paid and self.due_date:
            from django.utils import timezone

            today = timezone.now().date()
            return (today - self.due_date).days if today > self.due_date else 0
        return 0

    class Meta:
        ordering = ["due_date"]

    def __str__(self):
        return f"Debt for Invoice {self.invoice.number}"


__all__ = ["Invoice", "InvoiceLine", "Payment", "Debt"]
