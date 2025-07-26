# proizvodnja/signals.py

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.models.signals import (post_delete, post_migrate, post_save,
                                      pre_save)
from django.dispatch import receiver

from financije.models import FinancialDetails
from financije.services import (process_completed_work_order,
                                update_project_financials)
# Import iz ljudski_resursi (ako treba)
from ljudski_resursi.models import (  # ako imaš Evaluacija, inače ukloni
    Employee, Evaluacija)
from skladiste.models import Artikl

# Modelle iz proizvodnja.models:
from .models import (  # AnotherModel,  # Ukloni ili odkomentiraj ako doista postoji
    Angazman, DodatniAngazman, Notifikacija, Projekt, RadniNalog, Usteda,
    VideoMaterijal)

logger = logging.getLogger(__name__)


##############################################################################
# 1) PRE_SAVE HOOKS (store_original_status)
##############################################################################


@receiver(pre_save, sender=Projekt)
def store_original_status_projekt(sender, instance, **kwargs):
    """
    Ako je projekt već postojao, pamtimo stari status u _original_status
    radi kasnije usporedbe u post_save.
    """
    if instance.pk and not hasattr(instance, "_original_status"):
        try:
            original = sender.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except sender.DoesNotExist:
            instance._original_status = None
    else:
        instance._original_status = None


@receiver(pre_save, sender=RadniNalog)
def store_original_status_radni_nalog(sender, instance, **kwargs):
    """
    Slično, spremamo stari status radnog naloga ako pk postoji,
    pa kasnije u post_save možemo reagirati na promjenu statusa.
    """
    if instance.pk and not hasattr(instance, "_original_status"):
        try:
            original = sender.objects.get(pk=instance.pk)
            instance._original_status = original.status
        except sender.DoesNotExist:
            instance._original_status = None
    else:
        instance._original_status = None


##############################################################################
# 2) POST_SAVE HOOKS
##############################################################################


@receiver(post_save, sender=Projekt)
def obavijesti_o_promjeni_statusa_projekta(sender, instance, created, **kwargs):
    """
    Ako se status promijeni (vidi _original_status), kreiraj notifikaciju.
    """
    original_status = getattr(instance, "_original_status", None)
    current_status = instance.status

    # Samo ako se status promijenio
    if original_status != current_status:
        # Mapiramo neke statuse
        status_map = {
            "UPOZORENJE": {
                "poruka": f"Upozorenje! Projekt '{instance.naziv_projekta}' može kasniti.",
                "prioritet": "Srednji",
                "tip": "Upozorenje",
            },
            "UGROZEN": {
                "poruka": f"Ugrožen! Projekt '{instance.naziv_projekta}' je ozbiljno ugrožen!",
                "prioritet": "Visok",
                "tip": "Greška",
            },
            "PROBIJEN_ROK": {
                "poruka": f"Kašnjenje! Projekt '{instance.naziv_projekta}' je probio rok.",
                "prioritet": "Visok",
                "tip": "Greška",
            },
            "ZAVRSENO": {
                "poruka": f"Čestitke! Projekt '{instance.naziv_projekta}' je uspješno završen.",
                "prioritet": "Srednji",
                "tip": "Informacija",
            },
        }

        if current_status in status_map:
            data = status_map[current_status]
            # Ako projekt ima polje "odgovorna_osoba" (npr. Employee),
            # i ta osoba ima .user:
            korisnik = None
            # if getattr(instance, 'odgovorna_osoba', None):
            #     korisnik = instance.odgovorna_osoba.user

            if korisnik:  # Ako si doista definirao polje
                with transaction.atomic():
                    notifikacija = Notifikacija.objects.create(
                        korisnik=korisnik,
                        poruka=data["poruka"],
                        prioritet=data["prioritet"],
                        tip=data["tip"],
                    )
                    logger.debug(f"Notifikacija kreirana za promjenu statusa projekta: {instance.naziv_projekta}")

                    # Slanje notifikacije preko Channels
                    channel_layer = get_channel_layer()
                    if channel_layer:
                        try:
                            async_to_sync(channel_layer.group_send)(
                                f"notifikacije_{notifikacija.korisnik.id}",
                                {
                                    "type": "send_notification",
                                    "message": notifikacija.poruka,
                                },
                            )
                        except Exception as e:
                            logger.error(f"Failed to send notification: {e}")


@receiver(post_save, sender=Projekt)
def handle_design_requirements(sender, instance, created, **kwargs):
    """Handle design requirements for production projects"""
    if created:
        from projektiranje_app.models import DesignTask

        # Create associated design task if needed
        if instance.tip_vozila:
            DesignTask.objects.create(
                projekt=instance,
                status="draft",
                predvidjeni_sati_dizajna=instance.tip_vozila.get_default_design_hours(),
            )


@receiver(post_save, sender=RadniNalog)
def obavijesti_o_promjeni_statusa_radnog_naloga(sender, instance, created, **kwargs):
    """
    Ako radni nalog promijeni status, kreiraj notifikaciju.
    """
    original_status = getattr(instance, "_original_status", None)
    current_status = instance.status

    if original_status != current_status:
        status_map = {
            "CEKA_OCJENU": {
                "poruka": f"Radni nalog '{instance.naziv_naloga}' čeka ocjenu.",
                "prioritet": "Visok",
                "tip": "Upozorenje",
            },
            "ZATVORENO": {
                "poruka": f"Radni nalog '{instance.naziv_naloga}' je zatvoren.",
                "prioritet": "Srednji",
                "tip": "Informacija",
            },
        }
        if current_status in status_map:
            data = status_map[current_status]
            # Ako radni_nalog ima polje 'odgovorna_osoba' => prilagodi
            korisnik = None
            # if getattr(instance, 'odgovorna_osoba', None):
            #     korisnik = instance.odgovorna_osoba.user

            if korisnik:
                with transaction.atomic():
                    notifikacija = Notifikacija.objects.create(
                        korisnik=korisnik,
                        poruka=data["poruka"],
                        prioritet=data["prioritet"],
                        tip=data["tip"],
                    )
                    logger.debug(f"Notifikacija kreirana za radni nalog: {instance.naziv_naloga}")

                    channel_layer = get_channel_layer()
                    if channel_layer:
                        async_to_sync(channel_layer.group_send)(
                            f"notifikacije_{notifikacija.korisnik.id}",
                            {
                                "type": "send_notification",
                                "message": notifikacija.poruka,
                            },
                        )


@receiver(post_save, sender=RadniNalog)
def check_design_dependencies(sender, instance, created, **kwargs):
    """Ensure work order doesn't start before design is complete"""
    if created or instance.status == "U_TIJEKU":
        from projektiranje_app.models import DesignTask

        design_task = DesignTask.objects.filter(projekt=instance.projekt).first()
        if design_task and design_task.status != "done":
            instance.status = "CEKA_DIZAJN"
            instance.save()


@receiver(post_save, sender=RadniNalog)
def update_related_modules(sender, instance, created, **kwargs):
    if created:
        # Update skladište
        Artikl.objects.filter(radni_nalog=instance).update(status="reserved")

        # Update financije
        FinancialDetails.objects.create(
            related_work_order=instance,
            predicted_costs=instance.calculate_predicted_costs(),
        )


@receiver(post_save, sender=RadniNalog)
def handle_work_order_completion(sender, instance, **kwargs):
    if instance.status == "ZAVRSENO":
        process_completed_work_order(instance)


@receiver(post_save, sender=Projekt)
def handle_project_financials(sender, instance, **kwargs):
    update_project_financials(instance)


@receiver(post_save, sender=RadniNalog)
def handle_radni_nalog_save(sender, instance, created, **kwargs):
    if instance.status == "ZAVRSENO":
        # Ažuriraj statistike proizvodnje
        instance.proizvodnja.update_statistics()
        # Pokreni task za ažuriranje statusa
        update_proizvodnja_status.delay()


##############################################################################
# 3) post_save/post_delete za DodatniAngazman
##############################################################################


@receiver(post_save, sender=DodatniAngazman)
@receiver(post_delete, sender=DodatniAngazman)
def update_angazman_sati(sender, instance, **kwargs):
    """
    Kad se kreira/briše DodatniAngazman, ažuriraj Angazman.sati_rada, status ...
    """
    instance.angazman.azuriraj_status()
    instance.angazman.save()


@receiver(post_save, sender=Angazman)
def post_save_angazman(sender, instance, created, **kwargs):
    if created:
        logger.debug(f"Angazman created for radni_nalog: {instance.radni_nalog.pk}")


@receiver(post_save, sender=Usteda)
def post_save_usteda(sender, instance, created, **kwargs):
    if created:
        logger.debug(f"Ušteda kreirana za radni_nalog: {instance.radni_nalog.pk}")


##############################################################################
# 4) POST_MIGRATE - kreiranje defaultnih grupa
##############################################################################


@receiver(post_migrate)
def create_user_groups(sender, **kwargs):
    """
    Ako želiš kreirati osnovne grupe kad se migrira 'proizvodnja' app.
    """
    if sender.name == "proizvodnja":
        groups_to_create = ["direktor", "voditelj_proizvodnje"]
        for group_name in groups_to_create:
            grp, created = Group.objects.get_or_create(name=group_name)
            if created:
                logger.debug(f"Grupa '{group_name}' kreirana.")
            else:
                logger.debug(f"Grupa '{group_name}' već postoji.")
