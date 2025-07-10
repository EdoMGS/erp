from decimal import Decimal

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class DesignTask(models.Model):
    """
    Glavni dizajnerski zadatak – obuhvaća cjelokupni projekt projektiranja (npr. vatrogasno vozilo).
    Povezan je s proizvodnim projektom (modul 'proizvodnja').
    """

    STATUS_CHOICES = [
        ("draft", _("U pripremi")),
        ("in_progress", _("U izradi")),
        ("awaiting_approval", _("Čeka odobrenje")),
        ("approved", _("Odobreno")),
        ("done", _("Završeno")),
    ]

    projekt = models.ForeignKey(
        "proizvodnja.Projekt",
        on_delete=models.CASCADE,
        related_name="design_tasks",
        verbose_name=_("Projekt (iz proizvodnje)"),
    )
    projektant = models.ForeignKey(
        "ljudski_resursi.Employee",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Projektant"),
    )
    tip_vozila = models.ForeignKey(
        "proizvodnja.TipVozila",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Tip vozila"),
    )
    predvidjeni_sati_dizajna = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal("0.0"),
        verbose_name=_("Predviđeni sati dizajna"),
    )
    utroseni_sati = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=Decimal("0.0"),
        verbose_name=_("Utrošeni sati dizajna"),
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="draft", verbose_name=_("Status")
    )
    datum_pocetka = models.DateField(
        null=True, blank=True, verbose_name=_("Datum početka projektiranja")
    )
    datum_zavrsetka = models.DateField(
        null=True, blank=True, verbose_name=_("Datum završetka projektiranja")
    )
    napomena = models.TextField(
        blank=True, null=True, verbose_name=_("Napomena / opis dizajna")
    )
    # Polja za audit trail
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Datum kreiranja")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Datum posljednje izmjene")
    )
    # Integracija CAD dokumenata – npr. SolidWorks i AutoCAD nacrti
    solidworks_drawing = models.FileField(
        upload_to="design_drawings/solidworks/",
        null=True,
        blank=True,
        verbose_name=_("SolidWorks nacrt"),
    )
    autocad_drawing = models.FileField(
        upload_to="design_drawings/autocad/",
        null=True,
        blank=True,
        verbose_name=_("AutoCAD nacrt"),
    )

    class Meta:
        verbose_name = _("Dizajnerski zadatak")
        verbose_name_plural = _("Dizajnerski zadaci")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.projekt} - {self.get_status_display()}"

    def izracunaj_preostale_sate(self):
        return self.predvidjeni_sati_dizajna - self.utroseni_sati

    def zavrsi_dizajn(self):
        self.status = "done"
        self.datum_zavrsetka = timezone.now().date()
        self.save()


class DesignSegment(models.Model):
    """
    Predstavlja pojedinačne segmente dizajna unutar glavnog zadatka.
    Na primjer: podvozje, nadogradnja, cjevovod, električni sustav, pumpni sustav, itd.
    """

    SEGMENT_TYPE_CHOICES = [
        ("chassis", _("Podvozje")),
        ("superstructure", _("Nadogradnja")),
        ("pipeline", _("Cjevovod")),
        ("electrical", _("Električni sustav")),
        ("pump", _("Pumpni sustav")),
        ("other", _("Ostalo")),
    ]

    design_task = models.ForeignKey(
        DesignTask,
        on_delete=models.CASCADE,
        related_name="segments",
        verbose_name=_("Glavni zadatak projektiranja"),
    )
    segment_type = models.CharField(
        max_length=50, choices=SEGMENT_TYPE_CHOICES, verbose_name=_("Tip segmenta")
    )
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis segmenta"))
    planirani_sati = models.DecimalField(
        max_digits=5,
        decimal_places=1,
        default=Decimal("0.0"),
        verbose_name=_("Planirani sati za segment"),
    )
    utroseni_sati = models.DecimalField(
        max_digits=6,
        decimal_places=1,
        default=Decimal("0.0"),
        verbose_name=_("Utrošeni sati za segment"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Datum kreiranja segmenta")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Datum posljednje izmjene segmenta")
    )

    class Meta:
        verbose_name = _("Segment dizajna")
        verbose_name_plural = _("Segmenti dizajna")
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.get_segment_type_display()} za {self.design_task}"

    def izracunaj_preostale_sate(self):
        return self.planirani_sati - self.utroseni_sati


class BillOfMaterials(models.Model):
    """
    Glavni BOM model – može se primijeniti na cjelokupni dizajnerski zadatak ili samo na pojedinačne segmente.
    Time omogućavamo višerazinsku strukturu (glavni BOM i pod-BOM-ovi po segmentima).
    """

    design_task = models.ForeignKey(
        DesignTask,
        on_delete=models.CASCADE,
        related_name="bom_list",
        verbose_name=_("Glavni dizajnerski zadatak"),
    )
    # Ako se BOM odnosi samo na određeni segment, veza je postavljena; inače ostaviti null.
    design_segment = models.ForeignKey(
        DesignSegment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="bom_list",
        verbose_name=_("Segment dizajna"),
    )
    naziv = models.CharField(
        max_length=200, default="Glavni BOM", verbose_name=_("Naziv BOM-a")
    )
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis BOM-a"))
    status = models.CharField(
        max_length=50, default="draft", verbose_name=_("Status BOM-a")
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Datum kreiranja")
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Datum posljednje izmjene")
    )

    class Meta:
        verbose_name = _("BOM")
        verbose_name_plural = _("BOM-ovi")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.naziv} ({self.status})"


class BOMItem(models.Model):
    """
    Stavka unutar BOM-a – povezuje materijal (iz modula 'skladiste') s količinom.
    """

    bom = models.ForeignKey(
        BillOfMaterials,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("BOM"),
    )
    materijal = models.ForeignKey(
        "skladiste.Materijal",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Materijal"),
    )
    kolicina = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("1.00"),
        verbose_name=_("Količina"),
    )
    napomena = models.CharField(
        max_length=255, blank=True, null=True, verbose_name=_("Napomena")
    )

    class Meta:
        verbose_name = _("BOM stavka")
        verbose_name_plural = _("BOM stavke")

    def __str__(self):
        mat_name = self.materijal.naziv if self.materijal else "Nepoznato"
        return f"{mat_name} (x {self.kolicina})"


class CADDocument(models.Model):
    """
    Model za pohranu CAD dokumenata – integrira SolidWorks i AutoCAD nacrte.
    Dokument se može vezati uz cijeli dizajnerski zadatak ili samo na pojedini segment.
    """

    design_task = models.ForeignKey(
        DesignTask,
        on_delete=models.CASCADE,
        related_name="cad_documents",
        verbose_name=_("Dizajnerski zadatak"),
    )
    design_segment = models.ForeignKey(
        DesignSegment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="cad_documents",
        verbose_name=_("Segment dizajna"),
    )
    file = models.FileField(upload_to="cad_documents/", verbose_name=_("CAD dokument"))
    file_type = models.CharField(
        max_length=20,
        choices=[("solidworks", _("SolidWorks")), ("autocad", _("AutoCAD"))],
        verbose_name=_("Tip CAD dokumenta"),
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Datum uploada")
    )

    class Meta:
        verbose_name = _("CAD dokument")
        verbose_name_plural = _("CAD dokumenti")
        ordering = ["-uploaded_at"]

    def __str__(self):
        return f"{self.get_file_type_display()} dokument za {self.design_task}"


class DesignRevision(models.Model):
    """
    Evidencija revizija – bilježi promjene i revizije na dizajnerskim zadacima ili njihovim segmentima.
    """

    design_task = models.ForeignKey(
        DesignTask,
        on_delete=models.CASCADE,
        related_name="revisions",
        verbose_name=_("Dizajnerski zadatak"),
    )
    design_segment = models.ForeignKey(
        DesignSegment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="revisions",
        verbose_name=_("Segment dizajna"),
    )
    broj_revizije = models.PositiveIntegerField(
        default=1, verbose_name=_("Broj revizije")
    )
    opis = models.TextField(verbose_name=_("Opis promjena"))
    autor = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Autor revizije"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name=_("Datum revizije")
    )

    class Meta:
        verbose_name = _("Revizija")
        verbose_name_plural = _("Revizije")
        ordering = ["-created_at"]

    def __str__(self):
        target = self.design_segment if self.design_segment else self.design_task
        return f"Revizija {self.broj_revizije} za {target}"


class DynamicPlan(models.Model):
    """
    Dinamički plan (npr. Gantt plan) za praćenje izvršenja zadataka.
    Može biti vezan uz cijeli dizajnerski zadatak ili samo na njegov segment.
    """

    # Napomena: Ako se plan primjenjuje isključivo na cjelokupan zadatak, polje design_segment ostaje null.
    design_task = models.OneToOneField(
        DesignTask,
        on_delete=models.CASCADE,
        related_name="dynamic_plan",
        verbose_name=_("Dizajnerski zadatak"),
    )
    design_segment = models.OneToOneField(
        DesignSegment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="dynamic_plan",
        verbose_name=_("Segment dizajna"),
    )
    json_data = models.JSONField(
        blank=True, null=True, verbose_name=_("Gantt podaci (JSON)")
    )
    pocetak_plana = models.DateField(
        null=True, blank=True, verbose_name=_("Početak plana")
    )
    kraj_plana = models.DateField(null=True, blank=True, verbose_name=_("Kraj plana"))
    napomena = models.TextField(blank=True, null=True, verbose_name=_("Napomena"))
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name=_("Datum posljednje izmjene")
    )

    class Meta:
        verbose_name = _("Dinamički plan")
        verbose_name_plural = _("Dinamički planovi")
        ordering = ["-updated_at"]

    def __str__(self):
        target = self.design_segment if self.design_segment else self.design_task
        return f"Dinamički plan za {target}"
