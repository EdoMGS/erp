# project_root/proizvodnja/utils.py

import logging
from datetime import datetime
from decimal import Decimal

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Avg, Q
from django.shortcuts import render

# Ovako ispravno importamo iz 'proizvodnja.models':
from proizvodnja.models import PovijestPromjena

from financije.models import Municipality  # ako ih doista koristiš
from ljudski_resursi.models import Employee  # OK: Employee je u ljudski_resursi

logger = logging.getLogger("nalozi")


########################################
# 1. Access-Level Checking
########################################


def check_access_level(user, allowed_positions=None, allowed_hierarchies=None):
    if user.is_superuser:
        return True

    employee = getattr(user, "employee", None)
    if not employee:
        return False

    # Primjer provjere (adjust prema svojoj logici):
    if allowed_positions:
        if getattr(employee, "access_level", None) not in allowed_positions:
            return False

    # Provjera hijerarhije (ako treba)
    if allowed_hierarchies:
        position = getattr(employee, "position", None)
        hierarchical_level = getattr(position, "hierarchical_level", None)
        if not hierarchical_level:
            return False
        level_name = hierarchical_level.name
        if level_name not in allowed_hierarchies:
            return False

    return True


def protected_view(view, allowed_positions=None, allowed_hierarchies=None):
    """
    Dekorator za zaštitu pogleda prema 'check_access_level'.
    """

    def wrapped_view(request, *args, **kwargs):
        if not check_access_level(request.user, allowed_positions, allowed_hierarchies):
            return render(request, "errors/403.html", status=403)
        return view(request, *args, **kwargs)

    return wrapped_view


def is_management(user):
    """
    Npr. “Direktor”, “Administrator”, “Voditelj Projekta”...
    Prilagodi prema poljima u Employee.
    """
    try:
        return user.employee.access_level in [
            "Direktor",
            "Administrator",
            "Voditelj Projekta",
            "Voditelj Proizvodnje",
            "Nabava",
            "Projektant",
        ]
    except AttributeError:
        return False


def management_required(view_func):
    """
    Django-ov 'user_passes_test' dekorator, da se gleda `is_management`.
    """
    decorated_view_func = user_passes_test(is_management)(view_func)
    return decorated_view_func


########################################
# 2. Notification Utilities
########################################


def informiraj_korisnika(korisnik, poruka):
    """
    Šalje asinkrono notifikaciju korisniku putem Channels.
    """
    try:
        channel_layer = get_channel_layer()
        group_name = f"notifikacije_{korisnik.id}"
        async_to_sync(channel_layer.group_send)(
            group_name,
            {"type": "send_notification", "message": poruka},
        )
        logger.debug(f"Notification sent to user: {korisnik.username}")
    except Exception as e:
        logger.error(f"Error sending notification to {korisnik.username}: {str(e)}")


def informiraj_ocjenjivace(radni_nalog):
    """
    Primjer: obavijest svim voditeljima/direktorima da radni nalog treba evaluaciju.
    """
    try:
        ocjenjivaci = Employee.objects.filter(position__title__in=["Voditelj", "Direktor", "Administrativno osoblje"])
        for ocjenjivac in ocjenjivaci:
            if ocjenjivac.user:
                informiraj_korisnika(
                    ocjenjivac.user,
                    f"Evaluation required for work order: {radni_nalog.naziv_naloga}",
                )
    except Exception as e:
        logger.error(f"Error notifying evaluators: {str(e)}")


########################################
# 3. Logging & Project Status
########################################


def log_action(korisnik, objekt, akcija, dodatni_podaci=None):
    """
    Bilježi radnju u PovijestPromjena (generička).
    """
    try:
        povijest = PovijestPromjena(
            content_object=objekt,
            user=korisnik,
            promjene={"akcija": akcija, "podaci": dodatni_podaci or {}},
        )
        povijest.save()
        logger.debug(f"Logged: {akcija} for {objekt.__class__.__name__} (ID: {objekt.id}) by {korisnik.username}")
    except Exception as e:
        logger.error(f"Error logging action: {str(e)}")


def izracunaj_prosjek_ocjena(radni_nalog):
    """
    Primjer: prosjek ocjena radnog naloga (npr. OcjenaKvalitete).
    """
    try:
        prosjek = radni_nalog.ocjene_kvalitete.aggregate(avg=Avg("ocjena"))["avg"] or 0
        return round(prosjek, 2)
    except Exception as e:
        logger.error(f"Error calculating average score: {str(e)}")
        return 0


def izracunaj_status_projekta(projekt):
    """
    Primjer: custom logika za izračun statusa (možeš prilagoditi).
    """
    try:
        projekt.izracunaj_napredak()
        # Ovdje su polja 'predvidjeni_troskovi' i 'stvarni_troskovi'
        # ako postoji takva logika u projekt modelu
        getattr(projekt, "predvidjeni_troskovi", Decimal("0.00"))
        getattr(projekt, "stvarni_troskovi", Decimal("0.00"))

        danas = datetime.now().date()
        if projekt.rok_za_isporuku:
            (projekt.rok_za_isporuku - danas).days
        else:
            pass

        # tražimo još nezavršene radne naloge
        nezavrseni_nalozi = projekt.radni_nalozi.filter(~Q(status="ZAVRSENO"), is_active=True).exists()

        if projekt.rok_za_isporuku and danas > projekt.rok_za_isporuku and nezavrseni_nalozi:
            return "PROBIJEN_ROK"
        elif not nezavrseni_nalozi:
            return "ZAVRSENO"
        else:
            return "U_TIJEKU"
    except Exception as e:
        logger.error(f"Error calculating project status: {str(e)}")
        return "U_TIJEKU"


########################################
# 4. CSV/PDF Parsing, Tax, etc. (Primjeri)
########################################

# Ostali utility/imports:
# parse_csv, parse_pdf, fetch_tax_data, itd.
# Ovdje ostaviš ako ti treba, ili obrišeš ako ne koristiš.
