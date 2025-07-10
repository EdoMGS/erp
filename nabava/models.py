# nabava/models.py

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

##################################################
# 1) DOBAVLJAČI I NJIHOVE GRUPE
##################################################


class GrupaDobavljaca(models.Model):
    naziv = models.CharField(max_length=100, unique=True, verbose_name=_("Naziv grupe"))
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis"))
    is_active = models.BooleanField(default=True, verbose_name=_("Aktivno"))

    class Meta:
        verbose_name = _("Grupa dobavljača")
        verbose_name_plural = _("Grupe dobavljača")
        ordering = ["naziv"]

    def __str__(self):
        return self.naziv


class Dobavljac(models.Model):
    REJTING_CHOICES = [
        ("A", "A - Strateški partner"),
        ("B", "B - Preferirani dobavljač"),
        ("C", "C - Odobreni dobavljač"),
        ("D", "D - Novi/Neocijenjeni dobavljač"),
    ]

    naziv = models.CharField(max_length=200, verbose_name=_("Naziv dobavljača"))
    oib = models.CharField(max_length=11, unique=True, verbose_name=_("OIB"))
    adresa = models.CharField(max_length=200, verbose_name=_("Adresa"))
    grad = models.CharField(max_length=100, verbose_name=_("Grad"))
    drzava = models.CharField(max_length=100, verbose_name=_("Država"))
    email = models.EmailField(verbose_name=_("Email"))
    telefon = models.CharField(max_length=50, verbose_name=_("Telefon"))
    web = models.URLField(blank=True, null=True, verbose_name=_("Web stranica"))

    grupa = models.ForeignKey(
        GrupaDobavljaca,
        on_delete=models.PROTECT,
        related_name="dobavljaci",
        verbose_name=_("Grupa dobavljača"),
    )
    rejting = models.CharField(
        max_length=1, choices=REJTING_CHOICES, default="D", verbose_name=_("Rejting")
    )

    rok_placanja = models.PositiveIntegerField(
        default=30, verbose_name=_("Rok plaćanja (dana)")
    )
    popust = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Standardni popust (%)"),
    )

    is_active = models.BooleanField(default=True, verbose_name=_("Aktivno"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Dobavljač")
        verbose_name_plural = _("Dobavljači")
        ordering = ["naziv"]

    def __str__(self):
        return f"{self.naziv} ({self.get_rejting_display()})"


##################################################
# 2) PLAN NABAVE I ZAHTJEVI
##################################################


class ProcurementPlan(models.Model):
    project_name = models.CharField(max_length=200, verbose_name=_("Project Name"))
    item = models.CharField(max_length=200, verbose_name=_("Item/Material"))
    quantity = models.IntegerField(verbose_name=_("Quantity"))
    required_date = models.DateField(verbose_name=_("Required Date"))
    status = models.CharField(max_length=100, verbose_name=_("Status"))
    responsible_person = models.CharField(
        max_length=200, verbose_name=_("Responsible Person")
    )
    note = models.TextField(blank=True, null=True, verbose_name=_("Note"))

    # Dodatno polje za prioritet
    priority = models.CharField(
        max_length=20,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium",
        verbose_name=_("Prioritet"),
    )

    def __str__(self):
        return f"{self.project_name} - {self.item} (Plan)"


class ProcurementRequest(models.Model):
    procurement_plan = models.ForeignKey(
        ProcurementPlan, on_delete=models.CASCADE, verbose_name=_("Procurement Plan")
    )
    item = models.CharField(max_length=200, verbose_name=_("Item"))
    quantity = models.IntegerField(verbose_name=_("Quantity"))
    department = models.CharField(max_length=200, verbose_name=_("Department"))
    status = models.CharField(max_length=100, verbose_name=_("Status"))
    request_date = models.DateField(verbose_name=_("Request Date"))

    def __str__(self):
        return f"Request for {self.item} - {self.status}"


##################################################
# 3) PURCHASE ORDER (LINE ITEM PRISTUP)
##################################################


class PurchaseOrder(models.Model):
    """
    Glavna narudžba prema dobavljaču (line-item pristup).
    """

    ORDER_STATUS_CHOICES = [
        ("draft", "Draft"),
        ("sent", "Sent"),
        ("partially_received", "Partially Received"),
        ("received", "Fully Received"),
        ("cancelled", "Cancelled"),
    ]

    supplier = models.ForeignKey(
        Dobavljac,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Dobavljač"),
    )
    order_date = models.DateField(verbose_name=_("Order Date"), default=timezone.now)
    expected_delivery_date = models.DateField(
        null=True, blank=True, verbose_name=_("Expected Delivery")
    )
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default="draft",
        verbose_name=_("Status narudžbe"),
    )

    # Ako želiš povezati s radnim nalogom iz proizvodnje:
    work_order = models.ForeignKey(
        "proizvodnja.RadniNalog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="purchase_orders",  # Dodano explicit related_name
        verbose_name=_("Radni Nalog"),
    )

    is_jit = models.BooleanField(default=False, verbose_name=_("Just-In-Time?"))
    delivery_schedule = models.DateField(
        null=True, blank=True, verbose_name=_("Delivery Schedule")
    )

    reference_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Reference Price (€/unit)"),
    )
    agreed_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Agreed Price (€/unit)"),
    )
    justification_for_deviation = models.TextField(
        blank=True, null=True, verbose_name=_("Justification for price deviation")
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Date Created"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Date Updated"))

    def clean(self):
        # Provjera ako je odstupanje cijene iznad 20%
        if self.agreed_price and self.reference_price and self.reference_price > 0:
            if self.agreed_price > self.reference_price * Decimal("1.20"):
                if not self.justification_for_deviation:
                    raise ValidationError(
                        _(
                            "Agreed price is >20% above reference price. Justification required."
                        )
                    )

    def __str__(self):
        supplier_name = self.supplier.naziv if self.supplier else "Unknown"
        return f"PurchaseOrder #{self.id} - {supplier_name}"

    def total_order_amount(self):
        """
        Zbroj (quantity x unit_price) - discount po stavkama
        """
        total = Decimal("0.00")
        for line in self.lines.all():
            total += line.line_total()
        return total

    def is_fully_received(self):
        """
        Pomoćna metoda ako želiš označiti da je PO u potpunosti zaprimljen (u skladište).
        """
        for line in self.lines.all():
            if not line.is_fully_received():
                return False
        return True


class PurchaseOrderLine(models.Model):
    """
    Svaka stavka u PurchaseOrderu (više artikala).
    """

    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="lines",
        verbose_name=_("Purchase Order"),
    )
    artikl = models.ForeignKey(
        "skladiste.Artikl", on_delete=models.PROTECT, verbose_name=_("Artikl")
    )
    quantity = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Količina")
    )
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Jedinična cijena (€)"),
    )
    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Popust (%)"),
    )
    received_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        verbose_name=_("Zaprimljena količina"),
    )

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError(_("Količina mora biti veća od 0"))
        if self.unit_price < 0:
            raise ValidationError(_("Cijena ne može biti negativna"))

    def line_total(self):
        base = self.quantity * self.unit_price
        rabat = base * (self.discount / 100)
        return base - rabat

    def is_fully_received(self):
        return self.received_quantity >= self.quantity

    def __str__(self):
        return f"{self.artikl.naziv} x {self.quantity}"


##################################################
# 4) NARUDZBENICA (ako zelis odvojeno)
##################################################


class Narudzbenica(models.Model):
    """
    Ako želiš zadržati odvojenu klasu “Narudzbenica” (domaći naziv),
    pored PurchaseOrder-a.
    """

    NARUDZBENICA_STATUS = [
        ("draft", "U pripremi"),
        ("sent", "Poslano"),
        ("received", "Zaprimljeno"),
        ("cancelled", "Otkazano"),
    ]

    broj = models.CharField(max_length=20, verbose_name=_("Broj narudžbenice"))
    datum = models.DateField(verbose_name=_("Datum"))
    dobavljac = models.ForeignKey(
        "nabava.Dobavljac",
        on_delete=models.PROTECT,
        limit_choices_to={"is_active": True},
        verbose_name=_("Dobavljač"),
    )
    status = models.CharField(
        max_length=20,
        choices=NARUDZBENICA_STATUS,
        default="draft",
        verbose_name=_("Status"),
    )

    # M2M prema Artikl, preko “NarudzbenicaStavka”
    artikli = models.ManyToManyField(
        "skladiste.Artikl", through="NarudzbenicaStavka", verbose_name=_("Artikli")
    )

    # Modificirana veza prema Racun - dodali smo related_name
    racun = models.OneToOneField(
        "financije.Racun",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="narudzbenica",  # Dodano explicit related_name
        verbose_name=_("Povezani račun"),
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Narudžbenica {self.broj} - {self.dobavljac}"

    class Meta:
        verbose_name = _("Narudžbenica")
        verbose_name_plural = _("Narudžbenice")
        ordering = ["-datum", "broj"]

    def kreiraj_primku(self, user):
        """
        Creates a Primka (skladiste.Primka) when order is received.
        Pazi da “created_by” i polje ‘datum’ prilagodiš svojim potrebama.
        """
        from skladiste.models import Primka, PrimkaStavka

        primka = Primka.objects.create(
            broj_primke=f"PR-{self.broj}",
            datum=timezone.now(),
            dobavljac=self.dobavljac,
            napomena="Automatski kreirano iz narudžbenice",
            created_by=user,
        )

        for stavka in self.stavke.all():
            PrimkaStavka.objects.create(
                primka=primka,
                artikl=stavka.artikl,
                kolicina=stavka.kolicina,
                cijena=stavka.cijena,
            )

        # Ako sve uspješno, promijeni status:
        self.status = "received"
        self.save()

        return primka


class NarudzbenicaStavka(models.Model):
    """
    Line item za Narudzbenica
    """

    narudzbenica = models.ForeignKey(
        Narudzbenica,
        on_delete=models.CASCADE,
        related_name="stavke",
        verbose_name=_("Narudžbenica"),
    )
    artikl = models.ForeignKey(
        "skladiste.Artikl", on_delete=models.CASCADE, verbose_name=_("Artikl")
    )
    kolicina = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Količina")
    )
    cijena = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name=_("Cijena")
    )

    class Meta:
        verbose_name = _("Stavka narudžbenice")
        verbose_name_plural = _("Stavke narudžbenice")

    def __str__(self):
        return f"{self.artikl.naziv} - {self.kolicina}"

    def clean(self):
        if self.kolicina <= 0:
            raise ValidationError(_("Količina mora biti veća od 0"))
        if self.cijena < 0:
            raise ValidationError(_("Cijena ne može biti negativna"))

    def get_total(self):
        return self.kolicina * self.cijena
