# prodaja/models.py

from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

# Pretpostavljamo da BaseModel sadrži created_at, updated_at, is_active
from common.models import BaseModel
from proizvodnja.models import Projekt  # Povezan s proizvodnjom

# Import modela iz ostalih aplikacija (prilagodite namespace prema vašem projektu)
from projektiranje_app.models import CADDocument, DesignTask

# Financijska analiza – pretpostavljamo da postoji model u financije aplikaciji
# (ako nije definiran, ostavite kao stranicu za kasnije proširenje)
# from financije.models import FinancialAnalysis


########################################
# 1) PROJECT / SERVICE TYPE
########################################
class ProjectServiceType(models.Model):
    name = models.CharField(
        max_length=255, unique=True, verbose_name=_("Naziv usluge/projekta")
    )
    description = models.TextField(blank=True, null=True, verbose_name=_("Opis"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Project/Service Type")
        verbose_name_plural = _("Project/Service Types")


########################################
# 2) SALES OPPORTUNITY (LEAD)
########################################
class SalesOpportunity(models.Model):
    STAGE_CHOICES = [
        ("new", _("Novi lead")),
        ("qualified", _("Kvalificiran")),
        ("negotiation", _("Pregovori")),
        ("won", _("Zatvoren - dobiveno")),
        ("lost", _("Zatvoren - izgubljeno")),
    ]
    LEAD_SOURCE_CHOICES = [
        ("field_visit", _("Terenska posjeta")),
        ("tender", _("Javna nabava / natječaj")),
        ("referral", _("Preporuka postojećeg klijenta")),
        ("marketing", _("Digitalni marketing / kampanja")),
        ("trade_fair", _("Sajam / industrijski događaj")),
        ("other", _("Ostalo")),
    ]

    name = models.CharField(max_length=255, verbose_name=_("Naziv leada / prilike"))
    client = models.ForeignKey(
        "client_app.ClientSupplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Klijent (CRM)"),
    )
    lead_source = models.CharField(
        max_length=50,
        choices=LEAD_SOURCE_CHOICES,
        default="other",
        verbose_name=_("Izvor leada"),
    )
    stage = models.CharField(
        max_length=50,
        choices=STAGE_CHOICES,
        default="new",
        verbose_name=_("Faza prodajnog ciklusa"),
    )
    budget = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Budžet (procjena)"),
    )
    authority = models.BooleanField(
        default=False, verbose_name=_("Klijent ima ovlasti za potpis?")
    )
    need = models.BooleanField(default=False, verbose_name=_("Jasna potreba klijenta?"))
    timeframe = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Vremenski okvir (BANT)")
    )
    public_tender_number = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Broj javnog natječaja")
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Odgovorni prodajni predstavnik"),
    )
    project_service_type = models.ForeignKey(
        ProjectServiceType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Vrsta usluge/projekta"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Vrijeme kreiranja")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Zadnje ažuriranje")
    )
    amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Vrijednost")
    )
    notes = models.TextField(blank=True, verbose_name=_("Bilješke"))

    def __str__(self):
        return f"[{self.stage}] {self.name} - {self.client}"

    class Meta:
        verbose_name = _("Sales Opportunity (Lead)")
        verbose_name_plural = _("Sales Opportunities (Leads)")
        ordering = ["-created_at"]


########################################
# 3) FIELD VISIT
########################################
class FieldVisit(models.Model):
    opportunity = models.ForeignKey(
        SalesOpportunity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="field_visits",
        verbose_name=_("Povezana prilika"),
    )
    visited_client = models.CharField(
        max_length=255, verbose_name=_("Posjećeni klijent")
    )
    date_of_visit = models.DateField(verbose_name=_("Datum posjete"))
    purpose = models.TextField(
        blank=True, null=True, verbose_name=_("Svrha posjete / bilješke")
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Prodajni predstavnik"),
    )

    def __str__(self):
        return f"Terenska posjeta {self.visited_client} ({self.date_of_visit})"

    class Meta:
        verbose_name = _("Field Visit")
        verbose_name_plural = _("Field Visits")
        ordering = ["-date_of_visit"]


########################################
# 4) QUOTATION
########################################
class Quotation(models.Model):
    STATUS_CHOICES = [
        ("draft", _("Nacrt")),
        ("sent", _("Poslano klijentu")),
        ("approved", _("Odobreno")),
        ("rejected", _("Odbijeno")),
    ]

    client = models.ForeignKey(
        "client_app.ClientSupplier",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Klijent (CRM)"),
    )
    opportunity = models.ForeignKey(
        SalesOpportunity,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="quotations",
        verbose_name=_("Pripadajuća prilika (Opportunity)"),
    )
    quote_number = models.CharField(
        max_length=50, unique=True, verbose_name=_("Broj ponude")
    )
    valid_until = models.DateField(verbose_name=_("Vrijedi do"))
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status ponude"),
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Ukupan iznos (€)")
    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Popust (%)"),
    )
    revision_count = models.PositiveIntegerField(
        default=0, verbose_name=_("Broj revizija")
    )
    created_by = models.CharField(max_length=255, verbose_name=_("Kreirao/la"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    linked_production_order = models.ForeignKey(
        "proizvodnja.RadniNalog", null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return f"Quotation {self.quote_number} for {self.client}"


########################################
# 5) SALES ORDER
########################################
class SalesOrder(models.Model):
    STATUS_CHOICES = [
        ("pending", _("Na čekanju")),
        ("completed", _("Završeno")),
        ("cancelled", _("Otkazano")),
    ]

    client = models.CharField(max_length=255, verbose_name=_("Klijent"))
    order_number = models.CharField(
        max_length=50, unique=True, verbose_name=_("Broj narudžbe")
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
        verbose_name=_("Status narudžbe"),
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Ukupan iznos (€)")
    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Popust (%)"),
    )
    created_by = models.CharField(max_length=255, verbose_name=_("Kreirao/la"))
    quotation = models.ForeignKey(
        Quotation,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name=_("Iz ponude (Quotation)"),
    )
    date_approved_by_client = models.DateField(
        null=True, blank=True, verbose_name=_("Klijent potvrdio (datum)")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sales Order {self.order_number} for {self.client}"


########################################
# 6) SALES CONTRACT
########################################
class SalesContract(models.Model):
    STATUS_CHOICES = [
        ("draft", _("Nacrt")),
        ("active", _("Aktivan")),
        ("closed", _("Zatvoren")),
        ("cancelled", _("Otkazan")),
    ]

    client = models.CharField(max_length=255, verbose_name=_("Klijent"))
    contract_number = models.CharField(
        max_length=50, unique=True, verbose_name=_("Broj ugovora")
    )
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status ugovora"),
    )
    public_tender_number = models.CharField(
        max_length=100, blank=True, null=True, verbose_name=_("Broj javnog natječaja")
    )
    bank_guarantee_required = models.BooleanField(
        default=False, verbose_name=_("Bankarska garancija tražena?")
    )
    total_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name=_("Ukupan iznos (€)")
    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Popust (%)"),
    )
    sales_order = models.OneToOneField(
        SalesOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sales_contract",
        verbose_name=_("Povezana narudžba"),
    )
    delivery_schedule = models.TextField(
        null=True, blank=True, verbose_name=_("Raspored isporuke")
    )
    client_specific_reqs = models.TextField(
        null=True, blank=True, verbose_name=_("Posebni zahtjevi klijenta")
    )
    related_production_order = models.ForeignKey(
        "proizvodnja.RadniNalog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Povezani Radni Nalog (ako postoji)"),
    )
    created_by = models.CharField(max_length=255, verbose_name=_("Kreirao/la"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Sales Contract {self.contract_number} for {self.client}"


########################################
# 7) WORK ORDER INPUT
########################################
class WorkOrderInput(models.Model):
    radni_nalog = models.ForeignKey(
        "proizvodnja.RadniNalog",
        on_delete=models.CASCADE,
        related_name="work_order_inputs",
        verbose_name=_("Radni nalog"),
    )
    proizvod = models.CharField(max_length=255, verbose_name=_("Proizvod/Komponenta"))
    kolicina = models.PositiveIntegerField(verbose_name=_("Količina"))
    cijena = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Cijena (€)")
    )

    def __str__(self):
        return f"{self.proizvod} - {self.kolicina} x {self.cijena} €"

    class Meta:
        verbose_name = _("Work Order Input")
        verbose_name_plural = _("Work Order Inputs")


########################################
# 8) TENDER PREPARATION & DOCUMENTS
########################################


class TenderDocument(models.Model):
    """
    Model za pojedinačni dokument natječaja.
    Omogućuje učitavanje različitih dokumenata (PDF, Word, CAD, itd.)
    """

    tender_preparation = models.ForeignKey(
        "TenderPreparation",
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name=_("Tender priprema"),
    )
    file = models.FileField(upload_to="tender_documents/", verbose_name=_("Dokument"))
    description = models.TextField(
        blank=True, null=True, verbose_name=_("Opis dokumenta")
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Datum uploada")
    )

    class Meta:
        verbose_name = _("Dokument natječaja")
        verbose_name_plural = _("Dokumenti natječaja")
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"Dokument {self.pk}"


class TenderPreparationManager(models.Manager):
    def active_tenders(self):
        return self.filter(is_active=True)

    def pending_submissions(self):
        return self.filter(
            status="in_preparation", delivery_opening_datetime__gt=timezone.now()
        )

    def get_by_opportunity(self, opportunity_id):
        return self.get(opportunity_id=opportunity_id)


class TenderPreparation(BaseModel):
    """
    Model koji vodi kompletnu pripremu ponude za javni natječaj.
    Povezan je 1:1 sa SalesOpportunity (koja sadrži podatke o javnom natječaju).
    """

    STATUS_CHOICES = [
        ("draft", _("Nacrt")),
        ("in_preparation", _("U pripremi")),
        ("ready", _("Spremno za ponudu")),
        ("submitted", _("Podneseno")),
    ]

    opportunity = models.OneToOneField(
        SalesOpportunity,
        on_delete=models.CASCADE,
        related_name="tender_preparation",
        verbose_name=_("Prilika (natječaj)"),
    )
    # Poveznica s ponudbenim nacrtima (dokumentima koje izrađuje tehnički ured u projektiranje_app)
    proposal_drawings = models.ManyToManyField(
        CADDocument,
        blank=True,
        related_name="proposal_tender_preparations",
        verbose_name=_("Ponudbeni nacrti"),
    )
    tender_instructions = models.TextField(
        blank=True, null=True, verbose_name=_("Upute za ponuditelje")
    )
    evaluation_criteria = models.JSONField(
        blank=True, null=True, verbose_name=_("Kriteriji evaluacije")
    )
    tender_validity = models.DateField(
        blank=True, null=True, verbose_name=_("Rok valjanosti ponude")
    )
    delivery_opening_datetime = models.DateTimeField(
        blank=True, null=True, verbose_name=_("Datum i vrijeme otvaranja ponuda")
    )
    payment_terms = models.TextField(
        blank=True, null=True, verbose_name=_("Uvjeti plaćanja")
    )
    warranty_terms = models.TextField(
        blank=True, null=True, verbose_name=_("Uvjeti jamstva")
    )
    # Garancija za ozbiljnost ponude (obično 3%)
    seriousness_guarantee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("3.00"),
        verbose_name=_("Postotak garancije za ozbiljnost ponude"),
        help_text=_("Obično 3%"),
    )
    seriousness_guarantee_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Iznos garancije za ozbiljnost ponude"),
    )
    # Garancija za uredno izvršenje ugovora (obično 10%)
    performance_guarantee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("10.00"),
        verbose_name=_("Postotak garancije za uredno izvršenje ugovora"),
        help_text=_("Obično 10%"),
    )
    performance_guarantee_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Iznos garancije za uredno izvršenje ugovora"),
    )
    # Bankarska garancija za jamstveni rok – vrijednost se unosi (npr. 2-10%)
    warranty_guarantee_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Postotak bankarske garancije za jamstveni rok"),
        help_text=_("Unesite vrijednost u rasponu, npr. 2 do 10%"),
    )
    warranty_guarantee_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Iznos bankarske garancije za jamstveni rok"),
    )
    cashflow_plan = models.JSONField(
        blank=True, null=True, verbose_name=_("Plan cashflow-a")
    )
    nabava_updates = models.JSONField(
        blank=True, null=True, verbose_name=_("Ažurirane ponude materijala iz nabave")
    )
    notes = models.TextField(blank=True, null=True, verbose_name=_("Dodatne napomene"))
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status pripreme tendera"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Vrijeme kreiranja")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Zadnje ažuriranje")
    )

    # Kalkulacijski podaci
    material_costs = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Troškovi materijala"),
    )
    labor_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Radni sati"),
    )
    hourly_rate = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=Decimal("50.00"),
        verbose_name=_("Satnica (€)"),
    )
    required_documents = models.JSONField(
        default=dict, blank=True, verbose_name=_("Obavezna dokumentacija")
    )
    technical_specs = models.JSONField(
        default=dict, blank=True, verbose_name=_("Tehničke specifikacije")
    )

    # Poveznica s Projektiranjem
    technical_drawings = models.ManyToManyField(
        DesignTask,
        related_name="tenders",
        blank=True,
        verbose_name=_("Tehnički nacrti"),
    )
    project_manager = models.CharField(
        max_length=255, null=True, blank=True, verbose_name=_("Voditelj projekta (ime)")
    )
    # Poveznica s Proizvodnjom
    production_capacity = models.ForeignKey(
        Projekt,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Povezani projekt"),
    )
    estimated_production_time = models.DurationField(
        null=True, blank=True, verbose_name=_("Procijenjeno vrijeme proizvodnje")
    )
    # Poveznica s Financijama
    financial_analysis = models.OneToOneField(
        "financije.FinancialAnalysis",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tender",
        verbose_name=_("Financijska analiza"),
    )
    payment_schedule = models.JSONField(
        default=dict, blank=True, verbose_name=_("Plan plaćanja")
    )

    objects = TenderPreparationManager()

    def clean(self):
        if self.tender_validity and self.delivery_opening_datetime:
            if self.tender_validity < self.delivery_opening_datetime.date():
                raise ValidationError(
                    {"tender_validity": "Tender validity must be after opening date"}
                )

        if self.seriousness_guarantee_percentage > 100:
            raise ValidationError(
                {"seriousness_guarantee_percentage": "Percentage cannot exceed 100"}
            )

    # Kalkulacijske metode

    @property
    def total_labor_cost(self):
        """Izračunava ukupni trošak rada"""
        if self.labor_hours and self.hourly_rate:
            return self.labor_hours * self.hourly_rate
        return Decimal("0.00")

    def calculate_fixed_costs(self):
        """
        Izračunava fiksne mjesečne troškove (režije, administracija, krediti itd.).
        Ovdje se koriste fiksne vrijednosti, ali u praksi biste mogli povući podatke iz drugog modula ili postavki.
        """
        # Primjer fiksnih troškova – ovo možete zamijeniti s konfiguracijom iz financija
        fixed_costs = Decimal("2000.00")  # npr. ukupni fiksni troškovi po mjesecu
        # Ako postoji financijska analiza, možete dodati njene fiksne troškove
        if self.financial_analysis and hasattr(self.financial_analysis, "fixed_costs"):
            fixed_costs += self.financial_analysis.fixed_costs
        return fixed_costs

    def calculate_production_cost(self):
        """
        Ako je definiran proizvodni kapacitet (povezani projekt), poziva se metoda izračuna troška iz modula proizvodnje.
        """
        production_cost = Decimal("0.00")
        if self.production_capacity and hasattr(
            self.production_capacity, "calculate_cost"
        ):
            production_cost = self.production_capacity.calculate_cost(
                self.estimated_production_time
            )
        return production_cost

    def calculate_available_work_hours(self):
        """
        Izračunava raspoložive radne sate na temelju proizvodnog kapaciteta.
        Pretpostavlja se da proizvodni projekt ima polja 'worker_count' i 'monthly_hours'.
        """
        if (
            self.production_capacity
            and hasattr(self.production_capacity, "worker_count")
            and hasattr(self.production_capacity, "monthly_hours")
        ):
            return (
                self.production_capacity.worker_count
                * self.production_capacity.monthly_hours
            )
        # Default: npr. 7 radnika * 160 sati = 1120 sati
        return Decimal("1120")

    def calculate_total_cost(self):
        """
        Izračunava ukupni trošak tendera, uzimajući u obzir:
        - Troškove materijala
        - Troškove rada
        - Fiksne troškove
        - Troškove proizvodnje
        - Dodatne troškove iz financijske analize (ako postoje)
        """
        base_cost = (self.material_costs or Decimal("0.00")) + self.total_labor_cost
        fixed_costs = self.calculate_fixed_costs()
        production_cost = self.calculate_production_cost()
        financial_cost = Decimal("0.00")
        if self.financial_analysis and hasattr(self.financial_analysis, "total_cost"):
            financial_cost = self.financial_analysis.total_cost
        return base_cost + fixed_costs + production_cost + financial_cost

    def simulate_offer_price(self, margin_percentage):
        """
        Simulira konačnu ponudu na temelju marže.
        margin_percentage: postotak marže koji se primjenjuje (npr. 20 za 20%).
        """
        total = self.calculate_total_cost()
        return total * (1 + Decimal(margin_percentage) / Decimal("100"))

    def calculate_margin(self):
        """
        Izračunava maržu (ako postoji budžet) kao postotak razlike između budžeta iz prilike i ukupnih troškova.
        """
        if self.opportunity and self.opportunity.budget and self.calculate_total_cost():
            return (
                (self.opportunity.budget - self.calculate_total_cost())
                / self.opportunity.budget
            ) * 100
        return None

    def check_required_documents(self):
        """
        Provjerava potpunost obavezne dokumentacije.
        Vraća popis nedostajućih dokumenata.
        """
        if not self.required_documents:
            return []
        missing = []
        for doc in self.required_documents:
            if not self.documents.filter(description=doc.get("name")).exists():
                missing.append(doc.get("name"))
        return missing

    def calculate_guarantees(self):
        """
        Automatski izračunava sve vrste garancija na temelju budžeta iz SalesOpportunity.
        """
        if self.opportunity and self.opportunity.budget:
            budget = self.opportunity.budget
            self.seriousness_guarantee_amount = (
                budget * self.seriousness_guarantee_percentage
            ) / Decimal("100.00")
            self.performance_guarantee_amount = (
                budget * self.performance_guarantee_percentage
            ) / Decimal("100.00")
            if self.warranty_guarantee_percentage:
                self.warranty_guarantee_amount = (
                    budget * self.warranty_guarantee_percentage
                ) / Decimal("100.00")
        else:
            self.seriousness_guarantee_amount = None
            self.performance_guarantee_amount = None
            self.warranty_guarantee_amount = None

    def notify_departments(self):
        """
        Obavještava relevantne odjele (projektiranje, proizvodnja, financije) o novom ili ažuriranom tenderu.
        Ovdje se koristi send_mail – u praksi bi se mogla koristiti integracija s sustavom za notifikacije.
        """
        from django.core.mail import send_mail

        # Ovdje biste dohvatili kontakte odjela iz konfiguracije ili modela
        departments = {
            "projektiranje": ["projektiranje@tvrtka.com"],
            "proizvodnja": ["proizvodnja@tvrtka.com"],
            "financije": ["financije@tvrtka.com"],
        }

        for dept, contacts in departments.items():
            send_mail(
                subject=f"Novi tender {self.pk} zahtijeva vašu pažnju",
                message=f"Detalji tendera: {self}",
                from_email="erp@tvrtka.com",
                recipient_list=contacts,
            )

    def calculate_overall_offer(self, margin_percentage):
        """
        Kombinira sve kalkulacije i simulira konačnu ponudu s primijenjenom maržom.
        """
        total_cost = self.calculate_total_cost()
        simulated_price = self.simulate_offer_price(margin_percentage)
        return {
            "total_cost": total_cost,
            "simulated_offer_price": simulated_price,
            "margin_percentage": margin_percentage,
            "calculated_margin": self.calculate_margin(),
        }

    def status_change_allowed(self, new_status):
        valid_transitions = {
            "draft": ["in_preparation"],
            "in_preparation": ["ready", "draft"],
            "ready": ["submitted", "in_preparation"],
            "submitted": ["ready"],
        }
        return new_status in valid_transitions.get(self.status, [])

    def change_status(self, new_status, user=None):
        if not self.status_change_allowed(new_status):
            raise ValidationError(
                f"Invalid status transition from {self.status} to {new_status}"
            )

        old_status = self.status
        self.status = new_status
        self.save()

        # Log status change
        TenderStatusChange.objects.create(
            tender=self, old_status=old_status, new_status=new_status, changed_by=user
        )

    def save(self, *args, **kwargs):
        # Prije spremanja, izračunaj garancije
        self.calculate_guarantees()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Priprema tendera za {self.opportunity}"


class TenderStatusChange(models.Model):
    tender = models.ForeignKey(TenderPreparation, on_delete=models.CASCADE)
    old_status = models.CharField(max_length=50)
    new_status = models.CharField(max_length=50)
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]


########################################
# 9) TENDER MATERIAL, LABOR, COST, SUMMARY
########################################


class TenderMaterial(models.Model):
    tender = models.ForeignKey(
        TenderPreparation, on_delete=models.CASCADE, related_name="tender_materials"
    )
    item_name = models.CharField(max_length=255, verbose_name=_("Naziv materijala"))
    unit_price = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Cijena jedinice")
    )
    quantity = models.PositiveIntegerField(verbose_name=_("Količina"))
    tax = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("PDV (%)"),
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Ukupna cijena"),
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        self.total_price = (
            self.unit_price * self.quantity * (1 + self.tax / Decimal("100"))
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return self.item_name


class TenderLabor(models.Model):
    tender = models.ForeignKey(
        TenderPreparation, on_delete=models.CASCADE, related_name="tender_labor"
    )
    labor_category = models.CharField(max_length=255, verbose_name=_("Vrsta rada"))
    hours = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name=_("Broj sati")
    )
    hourly_rate = models.DecimalField(
        max_digits=6, decimal_places=2, verbose_name=_("Satnica (€)")
    )
    total_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Ukupni trošak"),
        blank=True,
        null=True,
    )

    def save(self, *args, **kwargs):
        self.total_cost = self.hours * self.hourly_rate
        super().save(*args, **kwargs)

    def __str__(self):
        return self.labor_category


class TenderCost(models.Model):
    COST_TYPE_CHOICES = [
        ("direct", _("Neposredni")),
        ("indirect", _("Posredni")),
    ]
    tender = models.ForeignKey(
        TenderPreparation, on_delete=models.CASCADE, related_name="tender_costs"
    )
    cost_name = models.CharField(max_length=255, verbose_name=_("Naziv troška"))
    cost_type = models.CharField(
        max_length=50, choices=COST_TYPE_CHOICES, verbose_name=_("Vrsta troška")
    )
    amount = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Iznos")
    )

    def __str__(self):
        return self.cost_name


class TenderSummary(models.Model):
    tender = models.OneToOneField(
        TenderPreparation, on_delete=models.CASCADE, related_name="tender_summary"
    )
    total_material_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    total_labor_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    total_direct_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    total_indirect_cost = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )
    final_price = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0.00")
    )

    def update_costs(self):
        self.total_material_cost = sum(
            material.total_price for material in self.tender.tender_materials.all()
        )
        self.total_labor_cost = sum(
            labor.total_cost for labor in self.tender.tender_labor.all()
        )
        self.total_direct_cost = sum(
            cost.project_cost for cost in self.tender.tender_neposredni_troskovi.all()
        )
        self.total_indirect_cost = sum(
            cost.project_cost for cost in self.tender.tender_posredni_troskovi.all()
        )
        self.calculate_final_price()
        self.save()

    def calculate_final_price(self):
        self.final_price = (
            self.total_material_cost
            + self.total_labor_cost
            + self.total_direct_cost
            + self.total_indirect_cost
        )

    def __str__(self):
        return f"Konačna cijena: {self.final_price} €"


class TenderRasclamba(BaseModel):
    tender = models.ForeignKey(
        TenderPreparation, on_delete=models.CASCADE, related_name="rasclamba_items"
    )
    naziv_stavke = models.CharField(max_length=255, verbose_name=_("Naziv stavke"))
    sati_rada = models.DecimalField(
        max_digits=8, decimal_places=2, verbose_name=_("Sati rada")
    )
    nas_materijal = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Naš materijal")
    )
    vanjska_usluga = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Vanjska usluga")
    )
    oprema_dijelovi = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Oprema/dijelovi")
    )
    dobavljac = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Dobavljač")
    )

    def __str__(self):
        return self.naziv_stavke


class TenderNeposredniTroskovi(BaseModel):
    tender = models.ForeignKey(
        TenderPreparation,
        on_delete=models.CASCADE,
        related_name="tender_neposredni_troskovi",
    )
    description = models.CharField(max_length=255, verbose_name=_("Opis troška"))
    monthly_cost = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Mjesečni trošak")
    )
    project_cost = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Trošak po projektu")
    )
    coefficient = models.DecimalField(
        max_digits=5, decimal_places=2, verbose_name=_("Koeficijent")
    )

    def __str__(self):
        return self.description


class TenderPosredniTroskovi(BaseModel):
    tender = models.ForeignKey(
        TenderPreparation,
        on_delete=models.CASCADE,
        related_name="tender_posredni_troskovi",
    )
    description = models.CharField(max_length=255, verbose_name=_("Opis troška"))
    monthly_cost = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Mjesečni trošak")
    )
    project_cost = models.DecimalField(
        max_digits=12, decimal_places=2, verbose_name=_("Trošak po projektu")
    )

    def __str__(self):
        return self.description
