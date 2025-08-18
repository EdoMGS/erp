from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from .models import CashFlow, Invoice, Overhead, InvoiceLine


class InvoiceService:
    @staticmethod
    @transaction.atomic
    def create_invoice(data):
        invoice = Invoice.objects.create(**data)
        # Create associated records
        CashFlow.objects.create(
            tip_transakcije="priljev",
            iznos=invoice.amount,
            opis=f"Invoice {invoice.invoice_number}",
            datum=invoice.issue_date,
        )
        return invoice

    @staticmethod
    def calculate_overdue_invoices():
        return Invoice.objects.filter(paid=False, due_date__lt=timezone.now().date())


class FinancialReportingService:
    @staticmethod
    def generate_monthly_report(year, month):
        # Implementation for monthly financial reporting
        pass


def calculate_project_costs(project):
    """
    Calculate total costs for a project including labor, materials and overhead
    """

    # Calculate labor costs
    labor_costs = Decimal("0.00")
    for nalog in project.radni_nalozi.all():
        for ang in nalog.angazmani.all():
            labor_costs += ang.sati_rada * ang.employee.calculate_total_salary()["base_salary"]

    # Calculate material costs
    material_costs = Decimal("0.00")
    for nalog in project.radni_nalozi.all():
        for mat in nalog.materijali_stavke.all():
            material_costs += mat.materijal.cijena * mat.kolicina

    # Get current overhead
    current_overhead = Overhead.objects.filter(
        godina=timezone.now().year,
        mjesec=timezone.now().month
    ).first()

    overhead_cost = Decimal("0.00")
    if current_overhead:
        overhead_per_hour = current_overhead.overhead_ukupno / current_overhead.mjesecni_kapacitet_sati
        total_hours = sum(
            ang.sati_rada
            for nalog in project.radni_nalozi.all()
            for ang in nalog.angazmani.all()
        )
        overhead_cost = overhead_per_hour * total_hours

    return {
        "labor_costs": labor_costs,
        "material_costs": material_costs,
        "overhead_costs": overhead_cost,
        "total_costs": labor_costs + material_costs + overhead_cost,
    }


def update_project_financials(project):
    """
    Update all financial details for a project
    """
    costs = calculate_project_costs(project)

    # Update FinancialDetails
    project.financial_details.actual_costs = costs["total_costs"]

    if project.financial_details.contracted_gross_price:
        project.financial_details.actual_profit = (
            project.financial_details.contracted_gross_price - costs["total_costs"]
        )

    project.financial_details.save()


def process_completed_work_order(work_order):
    """
    Handle financial processing when a work order is completed
    """
    # Calculate costs for this specific work order
    labor_cost = sum(
        ang.sati_rada * ang.employee.calculate_total_salary()["base_salary"] for ang in work_order.angazmani.all()
    )

    material_cost = sum(mat.materijal.cijena * mat.kolicina for mat in work_order.materijali_stavke.all())

    # Create financial transaction records
    from .models import FinancijskaTransakcija

    # Record labor cost
    FinancijskaTransakcija.objects.create(
        iznos=labor_cost,
        opis=f"Trošak rada za radni nalog {work_order.broj_naloga}",
        content_object=work_order,
    )

    # Record material cost
    if material_cost > 0:
        FinancijskaTransakcija.objects.create(
            iznos=material_cost,
            opis=f"Trošak materijala za radni nalog {work_order.broj_naloga}",
            content_object=work_order,
        )

    # Update project financials
    update_project_financials(work_order.projekt)


def calculate_work_order_savings(radni_nalog):
    """Calculate savings for a work order"""
    if not radni_nalog.predvidjeno_vrijeme or not radni_nalog.stvarno_vrijeme:
        return {"saved_hours": Decimal("0.00"), "bonus_amount": Decimal("0.00")}

    saved_hours = radni_nalog.predvidjeno_vrijeme - radni_nalog.stvarno_vrijeme
    if saved_hours <= 0:
        return {"saved_hours": Decimal("0.00"), "bonus_amount": Decimal("0.00")}

    # Calculate bonus based on saved hours
    bonus_rate = Decimal("50.00")  # Example: 50 per hour saved
    bonus_amount = saved_hours * bonus_rate

    return {"saved_hours": saved_hours, "bonus_amount": bonus_amount}


def calculate_production_costs(proizvodnja):
    """
    Calculate total costs for a production unit
    """
    costs = Decimal("0.00")

    # Sum costs from all work orders
    for nalog in proizvodnja.radni_nalozi.all():
        # Labor costs
        labor = sum(
            ang.sati_rada * ang.employee.calculate_total_salary()["base_salary"] for ang in nalog.angazmani.all()
        )

        # Material costs
        materials = sum(mat.materijal.cijena * mat.kolicina for mat in nalog.materijali_stavke.all())

        costs += labor + materials

    # Add overhead
    # Use Overhead model imported at top
    current_overhead = Overhead.objects.filter(
        godina=timezone.now().year,
        mjesec=timezone.now().month
    ).first()
    if current_overhead:
        total_hours = sum(ang.sati_rada for nalog in proizvodnja.radni_nalozi.all() for ang in nalog.angazmani.all())
        overhead_cost = (current_overhead.overhead_ukupno / current_overhead.mjesecni_kapacitet_sati) * total_hours
        costs += overhead_cost

    return costs


def create_interco_invoice(sender, receiver, asset, amount, vat_rate, sender_in_vat=True):
    """Create a simplified inter-company invoice using textual client name only."""
    from decimal import Decimal
    from django.utils import timezone
    import uuid

    applied_rate = vat_rate if sender_in_vat else Decimal('0.00')
    today = timezone.now().date()
    invoice = Invoice.objects.create(
        client_name=str(receiver),
        invoice_number=str(uuid.uuid4()),
        issue_date=today,
        due_date=today,
        pdv_rate=applied_rate,
        amount=amount,
    )
    descr = f"{asset}"
    if not sender_in_vat:
        descr += " nije u sustavu PDV-a"
    InvoiceLine.objects.create(
        invoice=invoice,
        description=descr,
        quantity=Decimal('1.00'),
        unit_price=amount,
        tax_rate=applied_rate,
    )
    return invoice
