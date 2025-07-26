# skladiste/models.py

from decimal import Decimal

from django.conf import settings
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


###############################################################################
# 1) ZONA, LOKACIJA, ARTIKL, ZALIHA
###############################################################################
class Zona(models.Model):
    """
    Opcijski model za podjelu skladišta u zone (regije, hale...).
    """

    naziv = models.CharField(max_length=100, verbose_name=_("Naziv zone"))
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis zone"))

    def __str__(self):
        return self.naziv


class Lokacija(models.Model):
    """
    Konkretnija lokacija (npr. polica, regal, hodnik) unutar zone.
    """

    naziv = models.CharField(max_length=100, verbose_name=_("Naziv lokacije"))
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis"))
    zona = models.ForeignKey(
        "skladiste.Zona",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Zona"),
    )

    def __str__(self):
        return self.naziv


class Kategorija(models.Model):
    naziv = models.CharField(max_length=100, unique=True, verbose_name=_("Naziv kategorije"))
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis"))
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name=_("Nadređena kategorija"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Aktivno"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Kategorija")
        verbose_name_plural = _("Kategorije")
        ordering = ["naziv"]

    def __str__(self):
        return self.naziv

    def get_full_path(self):
        path = [self.naziv]
        current = self
        while current.parent:
            current = current.parent
            path.append(current.naziv)
        return " > ".join(reversed(path))


class Artikl(models.Model):
    naziv = models.CharField(max_length=255, verbose_name=_("Naziv artikla"))
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis"))
    sifra = models.CharField(max_length=50, unique=True, verbose_name=_("Šifra artikla"))
    jm = models.CharField(max_length=20, verbose_name=_("Jedinica mjere"))
    min_kolicina = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Minimalna količina"),
    )
    trenutna_kolicina = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Trenutna količina"),
    )
    nabavna_cijena = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Nabavna cijena"),
    )
    prodajna_cijena = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("0.00"),
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Prodajna cijena"),
    )
    kategorija = models.ForeignKey(
        "Kategorija",
        on_delete=models.PROTECT,
        related_name="artikli",
        verbose_name=_("Kategorija"),
    )
    dobavljac = models.ForeignKey(
        "nabava.Dobavljac",  # Changed to string reference
        on_delete=models.PROTECT,
        related_name="artikli",
        verbose_name=_("Dobavljač"),
    )
    lokacija = models.ForeignKey(
        "Lokacija",
        on_delete=models.PROTECT,
        related_name="artikli",
        verbose_name=_("Lokacija"),
    )
    is_active = models.BooleanField(default=True, verbose_name=_("Aktivno"))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.naziv} ({self.sifra})"

    class Meta:
        verbose_name = _("Artikl")
        verbose_name_plural = _("Artikli")
        ordering = ["naziv"]


###############################################################################
# 2) MATERIJAL -> RADNI NALOG
###############################################################################
class Materijal(models.Model):
    """Materijal za proizvodnju."""

    artikl = models.OneToOneField(Artikl, on_delete=models.CASCADE, related_name="materijal")
    status = models.CharField(
        max_length=50,
        choices=[
            ("na_skladistu", "Na skladištu"),
            ("naruceno_dostava", "Naručeno - Čeka dostavu"),
            ("naruceno_placanje", "Naručeno - Čeka plaćanje"),
            ("nije_naruceno", "Nije naručeno"),
        ],
        default="nije_naruceno",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    naziv = models.CharField(max_length=255, verbose_name=_("Naziv materijala"))
    cijena = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Cijena"))
    kolicina = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Količina"))
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis"))
    datum_dostave = models.DateField(blank=True, null=True, verbose_name=_("Datum dostave"))
    current_stock = models.PositiveIntegerField(default=0)
    min_required_stock = models.PositiveIntegerField(default=0)

    narudzbenica = models.ForeignKey("nabava.Narudzbenica", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.naziv

    class Meta:
        verbose_name = _("Materijal")
        verbose_name_plural = _("Materijali")
        ordering = ["naziv"]


###############################################################################
# 4) ALAT, HTZ OPREMA
###############################################################################
class Alat(models.Model):
    """
    Jednostavno praćenje alata.
    “assigned_to” znači tko je trenutno zadužio alat (ljudski_resursi.Employee).
    """

    naziv = models.CharField(max_length=100, verbose_name=_("Naziv alata"))
    inventarski_broj = models.CharField(max_length=50, verbose_name=_("Inventarski broj"))
    zaduzen = models.BooleanField(default=False, verbose_name=_("Zadužen?"))
    is_assigned = models.BooleanField(default=False, verbose_name=_("Je li dodijeljen?"))

    # Referenca na Employee preko stringa da izbjegnemo kružni import:
    assigned_to = models.ForeignKey(
        "ljudski_resursi.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Zaduženi djelatnik"),
    )

    def __str__(self):
        return self.naziv


class HTZOprema(models.Model):
    """
    HTZ oprema (kacige, zaštitne naočale, rukavice...).
    """

    vrsta = models.CharField(max_length=100, verbose_name=_("Vrsta HTZ opreme"))
    stanje = models.CharField(max_length=50, verbose_name=_("Stanje"))
    is_assigned = models.BooleanField(default=False, verbose_name=_("Trenutačno zaduženo?"))
    htz_equipment_tracking = models.BooleanField(default=False, verbose_name=_("Praćenje zaduženja HTZ opreme"))

    assigned_to = models.ForeignKey(
        "ljudski_resursi.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Dodijeljeno djelatniku"),
    )

    def __str__(self):
        return f"{self.vrsta} - {self.stanje}"


###############################################################################
# 5) DNEVNIK DOGAĐAJA
###############################################################################
class DnevnikDogadaja(models.Model):
    """
    Log bilo kakvih događaja vezanih uz skladište (priljev robe, otpis, pomicanje...).
    """

    datum = models.DateTimeField(auto_now_add=True, verbose_name=_("Datum"))
    dogadaj = models.CharField(max_length=255, verbose_name=_("Događaj"))
    artikl = models.ForeignKey(
        Artikl,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="dnevnik_dogadaja",
        verbose_name=_("Artikl (ako se odnosi)"),
    )

    def __str__(self):
        return f"{self.datum} - {self.dogadaj}"


###############################################################################
# 6) OPCIJSKI: SKLADISTE RESURS (ako treba)
###############################################################################
class SkladisteResurs(models.Model):
    """
    Ako želiš dodatno pratiti neku drugu “resursnu opremu” u skladištu
    (različitu od “Alat” ili “HTZOprema”).
    """

    naziv = models.CharField(max_length=255, verbose_name=_("Naziv resursa"))
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis"))
    kolicina = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_("Količina"))
    lokacija = models.CharField(max_length=255, verbose_name=_("Lokacija"))

    def __str__(self):
        return self.naziv

    class Meta:
        verbose_name = _("Skladišni resurs")
        verbose_name_plural = _("Skladišni resursi")
        ordering = ["naziv"]


###############################################################################
# 7) PRIMKA I IZDATNICA
###############################################################################
class Primka(models.Model):
    """Model for receiving goods into warehouse"""

    broj_primke = models.CharField(max_length=20, unique=True, verbose_name=_("Broj primke"))
    datum = models.DateField(verbose_name=_("Datum primke"))
    dobavljac = models.ForeignKey("nabava.Dobavljac", on_delete=models.PROTECT, verbose_name=_("Dobavljač"))
    napomena = models.TextField(blank=True, null=True, verbose_name=_("Napomena"))
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_primke",
        verbose_name=_("Kreirao"),
    )

    class Meta:
        verbose_name = _("Primka")
        verbose_name_plural = _("Primke")
        ordering = ["-datum", "-broj_primke"]

    def __str__(self):
        return f"Primka {self.broj_primke} ({self.datum})"


class PrimkaStavka(models.Model):
    """Individual items on a receipt"""

    primka = models.ForeignKey(
        Primka,
        on_delete=models.CASCADE,
        related_name="stavke",
        verbose_name=_("Primka"),
    )
    artikl = models.ForeignKey("Artikl", on_delete=models.PROTECT, verbose_name=_("Artikl"))
    kolicina = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name=_("Količina"),
    )
    cijena = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.00"))],
        verbose_name=_("Cijena"),
    )

    class Meta:
        verbose_name = _("Stavka primke")
        verbose_name_plural = _("Stavke primke")

    def __str__(self):
        return f"{self.artikl.naziv} - {self.kolicina}"


class Izdatnica(models.Model):
    """Model for issuing goods from warehouse"""

    broj_izdatnice = models.CharField(max_length=20, unique=True, verbose_name=_("Broj izdatnice"))
    datum = models.DateField(verbose_name=_("Datum izdavanja"))
    preuzeo = models.ForeignKey(
        "ljudski_resursi.Employee",
        on_delete=models.PROTECT,
        related_name="preuzete_izdatnice",
        verbose_name=_("Preuzeo"),
    )
    napomena = models.TextField(blank=True, null=True, verbose_name=_("Napomena"))
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_izdatnice",
        verbose_name=_("Kreirao"),
    )

    class Meta:
        verbose_name = _("Izdatnica")
        verbose_name_plural = _("Izdatnice")
        ordering = ["-datum", "-broj_izdatnice"]

    def __str__(self):
        return f"Izdatnica {self.broj_izdatnice} ({self.datum})"


class IzdatnicaStavka(models.Model):
    """Individual items on an issue document"""

    izdatnica = models.ForeignKey(
        Izdatnica,
        on_delete=models.CASCADE,
        related_name="stavke",
        verbose_name=_("Izdatnica"),
    )
    artikl = models.ForeignKey("Artikl", on_delete=models.PROTECT, verbose_name=_("Artikl"))
    kolicina = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        verbose_name=_("Količina"),
    )

    class Meta:
        verbose_name = _("Stavka izdatnice")
        verbose_name_plural = _("Stavke izdatnice")

    def __str__(self):
        return f"{self.artikl.naziv} - {self.kolicina}"
