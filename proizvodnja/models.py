# proizvodnja/models.py

import logging
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from common.choices import OCJENE_CHOICES
from common.models import BaseModel
from financije.models import FinancialDetails  # i dalje ako treba
from skladiste.models import Artikl, Materijal

User = get_user_model()

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True

##############################################################################
# 1) TIP, PROJEKT, GRUPA POSLOVA
##############################################################################
class TipProjekta(BaseModel):
    naziv = models.CharField(max_length=255, unique=True, verbose_name=_("Naziv tipa projekta"))
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis"))
    aktivan = models.BooleanField(default=True)

    def __str__(self):
        return self.naziv

    class Meta:
        verbose_name = _("Tip Projekta")
        verbose_name_plural = _("Tipovi Projekata")
        ordering = ['naziv']


class TipVozila(BaseModel):
    naziv = models.CharField(max_length=255, unique=True, verbose_name=_("Naziv tipa vozila"))
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis"))
    aktivan = models.BooleanField(default=True)

    def __str__(self):
        return self.naziv

    class Meta:
        verbose_name = _("Tip Vozila")
        verbose_name_plural = _("Tipovi Vozila")
        ordering = ['naziv']


class GrupaPoslova(BaseModel):
    naziv = models.CharField(max_length=255, unique=True, verbose_name=_("Naziv grupe poslova"))
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis grupe poslova"))
    tip_projekta = models.ForeignKey(
        TipProjekta,
        on_delete=models.CASCADE,
        verbose_name=_("Tip Projekta")
    )

    def __str__(self):
        return self.naziv

    class Meta:
        verbose_name = _("Grupa Poslova")
        verbose_name_plural = _("Grupe Poslova")
        ordering = ['naziv']


##############################################################################
# 2) PROJEKT
##############################################################################
class Projekt(BaseModel):
    STATUSI_PROJEKTA = [
        ('OTVOREN', 'Otvoren'),
        ('U_TIJEKU', 'U tijeku'),
        ('UPOZORENJE', 'Upozorenje'),
        ('UGROZEN', 'Ugrožen'),
        ('PROBIJEN_ROK', 'Probijen rok'),
        ('ZAVRSENO', 'Završeno'),
    ]

    naziv_projekta = models.CharField(max_length=255, verbose_name=_("Naziv projekta"), db_index=True)
    erp_id = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("ERP ID"))
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis"))
    pocetak_projekta = models.DateField(null=True, blank=True, verbose_name=_("Datum početka"))
    rok_za_isporuku = models.DateField(null=True, blank=True, verbose_name=_("Rok za isporuku"))
    tip_projekta = models.ForeignKey(TipProjekta, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Tip Projekta"))
    tip_vozila = models.ForeignKey(TipVozila, on_delete=models.SET_NULL, null=True, blank=True, verbose_name=_("Tip Vozila"))
    status = models.CharField(
        max_length=20,
        choices=STATUSI_PROJEKTA,
        default='OTVOREN',
        verbose_name=_("Status Projekta")
    )
    ugradnja_na_lokaciji = models.BooleanField(default=False, verbose_name=_("Ugradnja na Lokaciji"))
    ručni_unos_radnih_naloga = models.BooleanField(default=False, verbose_name=_("Ručni Unos Radnih Naloga"))

    financial_details = models.OneToOneField(
        FinancialDetails,
        on_delete=models.CASCADE,
        related_name='proizvodnja_financial_details',
        verbose_name=_("Financijski Detalji")
    )

    logger = logging.getLogger(__name__)

    def __str__(self):
        return self.naziv_projekta

    class Meta:
        verbose_name = _("Projekt")
        verbose_name_plural = _("Projekti")
        ordering = ['-pocetak_projekta']

    def calculate_financials(self):
        """Delegate financial calculations to financije app"""
        from financije.services import update_project_financials
        update_project_financials(self)

    def calculate_actual_costs(self):
        """Use financije app services instead of duplicating logic"""
        from financije.services import calculate_project_costs
        return calculate_project_costs(self)

    def azuriraj_status(self):
        danas = timezone.now().date()
        if self.rok_za_isporuku and danas > self.rok_za_isporuku:
            self.status = 'PROBIJEN_ROK'
        self.save()

    def izracunaj_napredak(self):
        radni_nalozi = self.radni_nalozi.filter(is_active=True)
        if not radni_nalozi.exists():
            return 0
        return 0

    def clean(self):
        if (self.financial_details.contracted_gross_price is not None and
                self.financial_details.contracted_net_price is not None):
            if self.financial_details.contracted_gross_price < self.financial_details.contracted_net_price:
                raise ValidationError(_("Ugovorena cijena (bruto) ne može biti manja od (neto)."))


##############################################################################
# 3) TEMPLATE ZA RADNI NALOG
##############################################################################
class TemplateRadniNalog(models.Model):
    tip_projekta = models.ForeignKey(
        TipProjekta,
        on_delete=models.CASCADE,
        related_name='template_nalozi',
        verbose_name=_("Tip Projekta")
    )
    tip_vozila = models.ForeignKey(
        TipVozila,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='template_nalozi',
        verbose_name=_("Tip Vozila")
    )
    grupa_posla = models.ForeignKey(
        GrupaPoslova,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='template_nalozi',
        verbose_name=_("Grupa Poslova")
    )
    naziv_naloga = models.CharField(max_length=255, verbose_name=_("Naziv Naloga"))
    opis_naloga = models.TextField(blank=True, null=True, verbose_name=_("Opis Naloga"))
    default_predvidjeno_vrijeme = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name=_("Predviđeno Vrijeme"))
    broj_izvrsenja = models.PositiveIntegerField(default=0, verbose_name=_("Broj Izvršenja"))
    akumulirani_sati = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), verbose_name=_("Akumulirani Sati"))
    sort_index = models.PositiveIntegerField(default=0, verbose_name=_("Sort Index"))

    # Ako želiš M2M s Materijalima (putem intermediate table):
    materijali = models.ManyToManyField(
        'skladiste.Materijal',
        through='RadniNalogMaterijal',
        related_name='template_nalozi'
    )

    def __str__(self):
        return self.naziv_naloga

    class Meta:
        verbose_name = _("Template Radni Nalog")
        verbose_name_plural = _("Template Radni Nalozi")
        ordering = ['sort_index']

    def get_prosjecni_sati(self):
        if self.broj_izvrsenja > 0:
            return self.akumulirani_sati / self.broj_izvrsenja
        return Decimal('0.00')


##############################################################################
# 4) PROIZVODNJA (glavni objekt)
##############################################################################
class Proizvodnja(BaseModel):
    STATUS_CHOICES = [
        ('planirano', 'Planirano'),
        ('u_progresu', 'U progresu'),
        ('zavrseno', 'Završeno'),
    ]
    projekt = models.ForeignKey(
        Projekt,
        on_delete=models.CASCADE,
        related_name='proizvodnje',
        verbose_name=_("Projekt")
    )
    naziv = models.CharField(max_length=255, verbose_name=_("Naziv Proizvodnje"))
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis"))
    datum_pocetka = models.DateField(null=True, blank=True, verbose_name=_("Datum Početka"))
    datum_zavrsetka = models.DateField(null=True, blank=True, verbose_name=_("Datum Završetka"))
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default='planirano',
        verbose_name=_("Status Proizvodnje")
    )
    # M2M -> resursi (strojevi, ako treba)
    resursi = models.ManyToManyField(
        'ProizvodniResurs',
        blank=True,
        related_name='proizvodnje',  # Added explicit related_name
        verbose_name=_("Resursi")
    )
    radni_nalozi = models.ManyToManyField(
        'RadniNalog',
        related_name='proizvodnja_m2m',
        blank=True,
        verbose_name=_("Radni Nalozi")
    )

    def __str__(self):
        return self.naziv

    class Meta:
        verbose_name = _("Proizvodnja")
        verbose_name_plural = _("Proizvodnje")
        ordering = ['-datum_pocetka']


class ProizvodnjaStatistika(models.Model):
    """Track production statistics and KPIs"""
    proizvodnja = models.OneToOneField(
        Proizvodnja,
        on_delete=models.CASCADE,
        related_name='statistika'
    )
    ukupno_radnih_sati = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name=_("Ukupno radnih sati")
    )
    prosjecna_efikasnost = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Prosječna efikasnost")
    )
    broj_zavrsenih_naloga = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Broj završenih naloga")
    )
    prosjecna_ocjena = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Prosječna ocjena kvalitete")
    )

    def update_statistics(self):
        """Update all statistics"""
        self.ukupno_radnih_sati = sum(
            nalog.stvarno_vrijeme or 0 
            for nalog in self.proizvodnja.radni_nalozi.all()
        )
        
        finished_orders = self.proizvodnja.radni_nalozi.filter(status='ZAVRSENO')
        self.broj_zavrsenih_naloga = finished_orders.count()
        
        if finished_orders.exists():
            self.prosjecna_efikasnost = sum(
                nalog.performance_score or 0 for nalog in finished_orders
            ) / finished_orders.count()
            
            self.prosjecna_ocjena = sum(
                nalog.quality_score or 0 for nalog in finished_orders
            ) / finished_orders.count()
        
        self.save()


##############################################################################
# 5) RADNI NALOG
##############################################################################
class RadniNalog(BaseModel):
    STATUSI_NALOGA = [
        ('OTVOREN', 'Otvoren'),
        ('U_TIJEKU', 'U tijeku'),
        ('CEKA_OCJENU', 'Čeka ocjenu'),
        ('ZAVRSENO', 'Završeno'),
    ]
    PRIORITETI_CHOICES = [('visok', 'Visok'), ('srednji', 'Srednji'), ('nizak', 'Nizak')]
    TIP_POSLA_CHOICES = [
        ('instalacija', 'Instalacija'),
        ('održavanje', 'Održavanje'),
        ('popravak', 'Popravak'),
        ('drugo', 'Drugo'),
    ]

    naziv_naloga = models.CharField(max_length=255, db_index=True, verbose_name=_("Naziv Naloga"))
    projekt = models.ForeignKey(
        Projekt,
        on_delete=models.CASCADE,
        related_name="radni_nalozi",
        verbose_name=_("Projekt")
    )
    grupa_posla = models.ForeignKey(
        GrupaPoslova,
        on_delete=models.CASCADE,
        related_name="radni_nalozi",
        verbose_name=_("Grupa Poslova")
    )
    tip_posla = models.CharField(
        max_length=20,
        choices=TIP_POSLA_CHOICES,
        default='drugo',
        verbose_name=_("Tip Posla")
    )
    datum_pocetka = models.DateField(null=True, blank=True, verbose_name=_("Datum Početka"))
    datum_zavrsetka = models.DateField(null=True, blank=True, verbose_name=_("Datum Završetka"))
    postotak_napretka = models.PositiveIntegerField(default=0, verbose_name=_("Postotak Napretka"))
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis"))

    dodatne_osobe = models.ManyToManyField(
        'ljudski_resursi.Employee',
        blank=True,
        related_name="dodatni_nalozi",
        verbose_name=_("Dodatne Osobe")
    )
    # Tko je zadužen (User ili Employee?)
    zaduzena_osoba = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="zaduzeni_nalozi",
        verbose_name=_("Zadužena Osoba")
    )
    odgovorna_osoba = models.ForeignKey(
        'ljudski_resursi.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="odgovorna_nalozi",
        verbose_name=_("Odgovorna Osoba")
    )
    prioritet = models.CharField(
        max_length=10,
        choices=PRIORITETI_CHOICES,
        default='srednji',
        verbose_name=_("Prioritet")
    )
    bypass_materijala = models.BooleanField(default=False, verbose_name=_("Bypass Materijala"))
    dokumentacija_bypass = models.BooleanField(default=False, verbose_name=_("Dokumentacija Bypass"))
    status = models.CharField(
        max_length=30,
        choices=STATUSI_NALOGA,
        default='OTVOREN',
        verbose_name=_("Status Naloga")
    )

    template_nalog = models.ForeignKey(
        TemplateRadniNalog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instancirani_nalozi',
        verbose_name=_("Template Nalog")
    )
    predvidjeno_vrijeme = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name=_("Predviđeno Vrijeme"))
    stvarno_vrijeme = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, verbose_name=_("Stvarno Vrijeme"))

    preduvjeti = models.ManyToManyField(
        'self',
        blank=True,
        symmetrical=False,
        related_name='ovisni_nalozi',
        verbose_name=_("Preduvjeti")
    )

    proizvodnja = models.ForeignKey(
        Proizvodnja,
        on_delete=models.CASCADE,
        verbose_name=_("Proizvodnja")
    )
    broj_naloga = models.CharField(max_length=100, unique=True)

    # Materijali
    materijali = models.ManyToManyField(
        'skladiste.Materijal', 
        through='RadniNalogMaterijal',
        related_name='radni_nalozi'
    )

    # Jedan glavni employee
    employee = models.ForeignKey(
        'ljudski_resursi.Employee',
        on_delete=models.CASCADE,
        related_name='radni_nalozi'
    )

    # Gantt / dokumentacija reference
    gantogram = models.ForeignKey(
        "projektiranje_app.DynamicPlan",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='gantogram_radninalozi'
    )
    tehnicka_dokumentacija = models.ForeignKey(
        "projektiranje_app.CADDocument",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='radni_nalozi'
    )
    linked_plan = models.ForeignKey(
        "projektiranje_app.DynamicPlan",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='linkedplan_radninalozi'
    )
    linked_contract = models.ForeignKey(
        "prodaja.SalesContract",   # <----- OVDJE koristimo ‘prodaja’ umjesto ‘financije’
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = _("Radni Nalog")
        verbose_name_plural = _("Radni Nalozi")
        ordering = ['-datum_pocetka']

    def __str__(self):
        return self.naziv_naloga

    def can_start(self):
        unfinished = self.preduvjeti.filter(status__in=['OTVOREN','U_TIJEKU','CEKA_OCJENU'])
        return not unfinished.exists()

    def azuriraj_status(self):
        if not hasattr(self, '_status_updated'):
            self._status_updated = True
            if self.status in ['OTVOREN','U_TIJEKU']:
                if self.can_start():
                    if self.postotak_napretka >= 100:
                        self.status = 'ZAVRSENO'
                    else:
                        self.status = 'U_TIJEKU'
            self.save(update_fields=['status'])

    def get_gantt_data(self):
        deps = [n.pk for n in self.preduvjeti.all()]
        return {
            'id': self.pk,
            'name': self.naziv_naloga,
            'start_date': self.datum_pocetka.isoformat() if self.datum_pocetka else '',
            'end_date': self.datum_zavrsetka.isoformat() if self.datum_zavrsetka else '',
            'dependencies': deps,
            'progress': self.postotak_napretka,
            'status': self.status,
        }

    def complete_work_order(self):
        """When work order is finished, trigger evaluations and rewards"""
        if self.status == 'ZAVRSENO':
            from ljudski_resursi.models import Evaluacija, Nagrada

            # Create evaluation
            evaluation = Evaluacija.objects.create(
                employee=self.employee,
                radni_nalog=self, 
                evaluation_period=timezone.now().date()
            )
            
            # Create reward if criteria met
            if self.should_award_bonus():
                Nagrada.objects.create(
                    employee=self.employee,
                    radni_nalog=self,
                    iznos=self.calculate_bonus_amount(),
                    razlog="Uspješno završen radni nalog"
                )

    def clean(self):
        if self.datum_zavrsetka and self.datum_pocetka:
            if self.datum_zavrsetka < self.datum_pocetka:
                raise ValidationError({
                    'datum_zavrsetka': _('Datum završetka ne može biti prije datuma početka')
                })
        
        if self.postotak_napretka > 100:
            raise ValidationError({
                'postotak_napretka': _('Postotak napretka ne može biti veći od 100%')
            })
            
        if self.predvidjeno_vrijeme and self.predvidjeno_vrijeme < 0:
            raise ValidationError({
                'predvidjeno_vrijeme': _('Predviđeno vrijeme ne može biti negativno')
            })


##############################################################################
# 6) ANGAZMAN, RADNINALOGMATERIJAL, DODATNI ANGAZMAN
##############################################################################
class Angazman(BaseModel):
    STATUSI_ANGAZMANA = [
        ('ZAVRSEN', 'Završeno'),
        ('U_TIJEKU', 'U tijeku'),
    ]

    radni_nalog = models.ForeignKey(
        RadniNalog,
        on_delete=models.CASCADE,
        related_name='angazmani'
    )
    employee = models.ForeignKey(
        'ljudski_resursi.Employee',
        on_delete=models.CASCADE
    )
    sati_rada = models.DecimalField(
        default=Decimal('0.00'),
        max_digits=5,
        decimal_places=2
    )
    datum_angazmana = models.DateField(default=timezone.now)
    je_dodatni = models.BooleanField(default=False)
    razlog = models.TextField(blank=True, null=True)
    # Polje tko je odobrio, ako ga uopće trebaš:
    odobreno_od_koga = models.ForeignKey(
        'ljudski_resursi.Employee',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='angazmani_odobreni',
        verbose_name="Odobrio"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUSI_ANGAZMANA,
        default='U_TIJEKU'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["radni_nalog", "employee"], name="unique_radni_nalog_zaposlenik")
        ]
        indexes = [
            models.Index(fields=['radni_nalog', 'employee']),
            models.Index(fields=['status']),
        ]

    def clean(self):
        if self.sati_rada < 0:
            raise ValidationError(_("Sati rada ne mogu biti negativni."))
        if self.sati_rada > 24:
            raise ValidationError(_("Sati rada ne mogu biti veći od 24 za jedan dan."))

    def __str__(self):
        dodatno = " (Dodatni)" if self.je_dodatni else ""
        return f"{self.employee} - {self.radni_nalog} ({self.sati_rada}h){dodatno}"

    def azuriraj_status(self):
        if self.sati_rada > 0:
            self.status = 'ZAVRSEN'
        else:
            self.status = 'U_TIJEKU'


class RadniNalogMaterijal(models.Model):
    radni_nalog = models.ForeignKey(
        RadniNalog,
        on_delete=models.CASCADE,
        related_name='materijali_stavke'
    )
    materijal = models.ForeignKey(  # This is the correct field name
        'skladiste.Materijal',
        on_delete=models.PROTECT,
        related_name='radni_nalozi_stavke'
    )
    template_nalog = models.ForeignKey(
        TemplateRadniNalog,
        on_delete=models.CASCADE,
        related_name='materijali_stavke',
        null=True,
        blank=True
    )
    kolicina = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.materijal} x {self.kolicina} za {self.radni_nalog or self.template_nalog}"

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(radni_nalog__isnull=False, template_nalog__isnull=True) |
                    models.Q(radni_nalog__isnull=True, template_nalog__isnull=False)
                ),
                name='one_parent_only'
            )
        ]


class DodatniAngazman(BaseModel):
    angazman = models.ForeignKey(
        Angazman,
        on_delete=models.CASCADE,
        related_name="dodatni_angazmani"
    )
    employee = models.ForeignKey(
        'ljudski_resursi.Employee',
        on_delete=models.CASCADE,
        related_name='dodatni_angazmani_zaposlenik'
    )
    sati_rada = models.DecimalField(
        default=Decimal('0.00'),
        max_digits=5,
        decimal_places=2
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["angazman", "employee"], name="unique_angazman_zaposlenik")
        ]
        indexes = [
            models.Index(fields=['angazman', 'employee']),
        ]

    def clean(self):
        if self.sati_rada < 0 or self.sati_rada > 24:
            raise ValidationError(_("Sati rada moraju biti između 0 i 24."))

    def __str__(self):
        return f"{self.employee} - {self.angazman} ({self.sati_rada}h)"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.angazman.azuriraj_status()
        self.angazman.save()


##############################################################################
# 7) OCJENA KVALITETE, VIDEO MATERIJAL/PITANJE (removed Nagrada)
##############################################################################
# Removed or commented out since it's now in ljudski_resursi
# class OcjenaKvalitete(models.Model):
#     ...

class VideoMaterijal(BaseModel):
    radni_nalog = models.ForeignKey(
        RadniNalog,
        on_delete=models.CASCADE,
        related_name="video_materijali"
    )
    naziv = models.CharField(max_length=255, db_index=True)
    opis = models.TextField(blank=True)
    video_file = models.FileField(upload_to='ocjene/videozapisi/')
    datum_dodavanja = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.video_file:
            max_size_mb = 50
            if self.video_file.size > max_size_mb * 1024 * 1024:
                raise ValidationError(_("Veličina video datoteke > 50 MB."))
            ext = self.video_file.name.lower().rsplit('.', 1)[-1]
            if ext not in ('mp4','avi','mkv'):
                raise ValidationError(_("Dopušteni formati su: mp4, avi, mkv."))

    def __str__(self):
        return f"{self.naziv} (Radni nalog: {self.radni_nalog_id})"

    class Meta:
        ordering = ['-datum_dodavanja']
        indexes = [models.Index(fields=['naziv', 'radni_nalog'])]


class VideoPitanje(BaseModel):
    radni_nalog = models.ForeignKey(
        RadniNalog,
        on_delete=models.CASCADE,
        related_name="video_pitanja"
    )
    video = models.FileField(upload_to="video_pitanja/", help_text=_("Video datoteka za pitanje."))
    opis = models.TextField(blank=True, null=True, help_text=_("Dodatne informacije o video pitanju."))

    def __str__(self):
        return f"Pitanje za {self.radni_nalog} (ID: {self.pk})"

    class Meta:
        indexes = [models.Index(fields=['radni_nalog'])]


class OcjenaKvalitete(models.Model):
    """
    Ocjene kvalitete za radne naloge - tehničke ocjene vezane uz izvršenje posla
    """
    radni_nalog = models.ForeignKey('RadniNalog', on_delete=models.CASCADE)
    ocjenjivac = models.ForeignKey(
        'ljudski_resursi.Employee', 
        on_delete=models.CASCADE,
        null=True, 
        blank=True,
    )
    employee = models.ForeignKey('ljudski_resursi.Employee', 
                               related_name='primljene_ocjene',
                               on_delete=models.CASCADE)
    
    # Core metrics (1-5 scale)
    kvaliteta_izvedbe = models.IntegerField(choices=OCJENE_CHOICES, default=3)
    postivanje_procedura = models.IntegerField(choices=OCJENE_CHOICES, default=3)
    efikasnost_rada = models.IntegerField(choices=OCJENE_CHOICES, default=3)
    
    # Time tracking
    predvidjeno_vrijeme = models.DecimalField(max_digits=6, decimal_places=2)
    stvarno_vrijeme = models.DecimalField(max_digits=6, decimal_places=2)
    
    # Media fields
    slike = models.ImageField(
        upload_to='ocjene/slike/',
        blank=True,
        null=True,
        verbose_name=_("Priložene slike"),
        help_text=_("Dopuštene ekstenzije: .jpg, .png")
    )
    video = models.FileField(
        upload_to='ocjene/videozapisi/',
        blank=True,
        null=True,
        verbose_name=_("Priloženi video"),
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'avi', 'mkv'])],
        help_text=_("Podržani formati: mp4, avi, mkv.")
    )
    
    komentar = models.TextField()
    datum_ocjene = models.DateTimeField(auto_now_add=True)
    tezinski_faktor = models.FloatField(default=1.0)
    
    class Meta:
        verbose_name = "Ocjena kvalitete"
        verbose_name_plural = "Ocjene kvalitete"


##############################################################################
# 8) NOTIFIKACIJE, POVIJEST, MJESEČNI WORK RECORD, UŠTEDA
##############################################################################
class Notifikacija(BaseModel):
    PRIORITETI = [("Visok", _("Visok")), ("Srednji", _("Srednji")), ("Nizak", _("Nizak"))]
    TIPOVI = [
        ("Informacija", _("Informacija")),
        ("Upozorenje", _("Upozorenje")),
        ("Greška", _("Greška")),
        ("Nagrada", _("Nagrada")),
    ]

    korisnik = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifikacije"
    )
    poruka = models.TextField()
    procitano = models.BooleanField(default=False)
    datum_stvaranja = models.DateTimeField(default=timezone.now)
    prioritet = models.CharField(
        max_length=20,
        choices=PRIORITETI,
        default="Nizak"
    )
    tip = models.CharField(
        max_length=50,
        choices=TIPOVI,
        default="Informacija"
    )

    class Meta:
        ordering = ["-datum_stvaranja"]
        indexes = [models.Index(fields=['korisnik', 'prioritet', 'tip'])]

    def oznaci_kao_procitano(self):
        if not self.procitano:
            self.procitano = True
            self.save()

    def __str__(self):
        return f"Notifikacija za {self.korisnik.username} - Prioritet: {self.prioritet}"


class PovijestPromjena(BaseModel):
    radni_nalog = models.ForeignKey(
        RadniNalog,
        on_delete=models.CASCADE,
        related_name='promjene'
    )
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField()
    object_ref = GenericForeignKey('content_type', 'object_id')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    promjene = models.JSONField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=['content_type', 'object_id'])]

    def __str__(self):
        return f"Promjene za {self.content_type} (ID: {self.object_id})"

    @classmethod
    def dodaj_promjenu(cls, content_object, user, promjene):
        cls.objects.create(
            content_type=ContentType.objects.get_for_model(content_object),
            object_id=content_object.pk,
            user=user,
            promjene=promjene,
        )


class MonthlyWorkRecord(BaseModel):
    employee = models.ForeignKey(
        'ljudski_resursi.Employee',
        on_delete=models.CASCADE,
        related_name="monthly_work_records"
    )
    year = models.PositiveIntegerField()
    month = models.PositiveIntegerField()
    hours_worked = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'))

    class Meta:
        unique_together = ('employee', 'year', 'month')
        indexes = [models.Index(fields=['employee', 'year', 'month'])]

    def __str__(self):
        return f"{self.employee} - {self.month}/{self.year} - {self.hours_worked} sati"

    def clean(self):
        if self.hours_worked < 0:
            raise ValidationError(_("Odrađeni sati ne mogu biti negativni."))
        if self.hours_worked > 300:
            raise ValidationError(_("Odrađeni sati ne mogu biti veći od 300 po mjesecu."))

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Usteda(BaseModel):
    radni_nalog = models.OneToOneField(
        RadniNalog,
        on_delete=models.CASCADE,
        related_name="usteda"
    )
    predvidjeno_vrijeme = models.DecimalField(max_digits=10, decimal_places=2)
    stvarno_vrijeme = models.DecimalField(max_digits=10, decimal_places=2)
    usteda_sati = models.DecimalField(default=0, max_digits=10, decimal_places=2)
    dodatna_nagrada = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def izracunaj_ustedu(self):
        """Delegate savings calculations to financije app"""
        from financije.services import calculate_work_order_savings
        result = calculate_work_order_savings(self.radni_nalog)
        self.usteda_sati = result['saved_hours']
        self.dodatna_nagrada = result['bonus_amount']
        self.save()

    def __str__(self):
        return f"Ušteda {self.usteda_sati}h za {self.radni_nalog}"


##############################################################################
# 9) PROIZVODNI RESURS (npr. stroj/linija/kapacitet)
##############################################################################
class ProizvodniResurs(models.Model):
    """
    Predstavlja stroj/liniju/radno mjesto u proizvodnji (za planiranje).
    NE isto što i "SkladisteResurs" (inventar) iz 'skladiste' app.
    """
    naziv = models.CharField(max_length=255, verbose_name=_("Naziv resursa"))
    tip = models.CharField(
        max_length=100,
        choices=[
            ('materijal', 'Materijal'),
            ('alat', 'Alat'),
            ('radna_linija', 'Radna linija/stroj'),
        ],
        default='radna_linija'
    )
    opis = models.TextField(blank=True, null=True, verbose_name=_("Opis resursa"))
    dostupnost = models.BooleanField(default=True, verbose_name=_("Dostupnost"))
    kolicina = models.PositiveIntegerField(default=0)

    # Changed from radni_nalog to proizvodnja
    proizvodnja = models.ForeignKey(
        Proizvodnja,
        on_delete=models.CASCADE,
        related_name='proizvodni_resursi',  # Changed from 'resursi' to 'proizvodni_resursi'
        verbose_name=_("Proizvodnja")
    )

    # Updated related_name
    linked_sales_contract = models.ForeignKey(
        'prodaja.SalesContract',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='linked_proizvodni_resursi'
    )

    def __str__(self):
        return self.naziv

    class Meta:
        verbose_name = _("Proizvodni Resurs")
        verbose_name_plural = _("Proizvodni Resursi")
        ordering = ['naziv']
