"""Kleine Hilfsfunktionen, die mehrere Formeln brauchen."""

from datetime import date

from numpy import asarray, floor, round as runden
from openfisca_core.errors import SituationParsingError

# Standardwert für ein nicht angegebenes Datum. Für Kinder sind Geburtsdatum,
# Betreuungsbeginn und Gesuchsdatum Pflicht; fehlt eines, bricht die
# Berechnung ab (kibg_alter_monate, kibg_beitragsbeginn).
DATUM_FEHLT = date(9999, 12, 31)
GEBURTSDATUM_FEHLT = DATUM_FEHLT

# Vollzugsbeginn von KiBG und KiBV: «ab ●●» (Ziff. IV KiBG und KiBV, Entwurf).
# Platzhalter nach Entscheid O1; muss mit formula_2028_08 und den Daten der
# Parameter übereinstimmen.
VOLLZUGSBEGINN = date(2028, 8, 1)


def plus_monate(datum, monate):
    """Ende einer Frist in Monaten (Annahme A7, sinngemäss Art. 77 OR).

    Die Frist endet am Tag mit derselben Zahl; gibt es diesen Tag im letzten
    Monat nicht, am letzten Tag dieses Monats.
    """
    jahr, monat = divmod(datum.month - 1 + monate, 12)
    jahr, monat = datum.year + jahr, monat + 1
    letzter_tag = (date(jahr + monat // 12, monat % 12 + 1, 1) - date.resolution).day
    return date(jahr, monat, min(datum.day, letzter_tag))


def formel_anhang(max_v, z1, z2, faktor):
    """Formel im Anhang der KiBV (Entwurf), auf die Art. 13 KiBV verweist.

        B = (MaxV + Z1) × (1 − (ME − MinmE) / (MaxmE − MinmE)) + Z2

    B: Beitrag je Kind und Betreuungsstunde; MaxV: höchster Beitrag je Kind und
    Betreuungsstunde; Z1: einkommensabhängiger und Z2: einkommensunabhängiger
    Zusatzbeitrag der politischen Gemeinde. `faktor` ist der Klammerausdruck
    1 − (ME − MinmE) / (MaxmE − MinmE), begrenzt nach Art. 15 KiBV
    (kibg_einkommensfaktor).

    Die Formel steht im Text nur einmal und deshalb auch im Code nur hier.
    """
    return (max_v + z1) * faktor + z2


def eingabefehler(population, betroffen, variable, meldung):
    """Bricht die Berechnung mit einer Fehlermeldung ab.

    Für Angaben, ohne die der Text nicht angewendet werden kann. Die Web-API
    gibt die Meldung als Fehler 400 an das Interface zurück, statt einen
    Betrag zu berechnen.
    """
    if betroffen.any():
        erste_id = asarray(population.ids)[betroffen][0]
        raise SituationParsingError(
            [population.entity.plural, erste_id, variable], meldung
        )


def monate_seit(datum, period):
    """Volle Monate von `datum` bis zum ersten Tag der Periode.

    Stichtag ist der erste Tag des Monats (Annahme A1 in challenge/szenarien.md).
    Gleiches Vorgehen wie bei `age` im OpenFisca-Template.
    """
    jahr = datum.astype("datetime64[Y]").astype(int) + 1970
    monat = datum.astype("datetime64[M]").astype(int) % 12 + 1
    tag = (datum - datum.astype("datetime64[M]") + 1).astype(int)
    monate = (period.start.year - jahr) * 12 + (period.start.month - monat)
    # Ist der Tag im Monat noch nicht erreicht, ist der letzte Monat nicht voll.
    return monate - (tag > period.start.day)


def volle_jahre_seit(datum, period):
    """Volle Jahre von `datum` bis zum ersten Tag der Periode."""
    return monate_seit(datum, period) // 12


def mindestens(wert, grenze):
    """Vergleich `wert >= grenze` mit kleiner Toleranz.

    OpenFisca speichert Zahlen als float32: 0.7 ist intern etwas kleiner als 0.7.
    """
    return wert >= grenze - 0.000001


def auf_rappen_runden(franken, schritt):
    """Kaufmännisch auf `schritt` Franken runden (5 Rappen, Annahme A4).

    Gerechnet wird in Rappen, damit Fälle wie 274.025 nicht wegen float32
    falsch abgerundet werden.
    """
    rappen = runden(franken.astype("float64") * 100, 2)
    schritt_rappen = round(schritt * 100)
    return floor(rappen / schritt_rappen + 0.5) * schritt_rappen / 100


def monatserster(jahr, monat):
    """Erster Tag des Monats `monat` im Jahr `jahr` (Arrays von Zahlen)."""
    return (
        ((jahr - 1970) * 12 + (monat - 1))
        .astype("datetime64[M]")
        .astype("datetime64[D]")
    )


def ende_nach_monaten(beginn, monate):
    """Letzter Tag eines Zeitraums von `monate` Monaten ab `beginn` (Arrays).

    Zwölf Monate ab dem 1. August 2028 dauern bis zum 31. Juli 2029; ab dem
    15. März 2029 bis zum 14. März 2030. Anders als eine Frist (plus_monate,
    A7) endet ein Zeitraum am Tag vor der gleichen Zahl.
    """
    monatsbeginn = beginn.astype("datetime64[M]")
    tag_im_monat = beginn - monatsbeginn.astype("datetime64[D]")
    gleicher_tag = (monatsbeginn + monate).astype("datetime64[D]") + tag_im_monat
    return gleicher_tag - 1


def jahr_und_monat(datum):
    """Jahr und Monat (1 bis 12) eines Datums-Arrays."""
    jahr = datum.astype("datetime64[Y]").astype(int) + 1970
    monat = datum.astype("datetime64[M]").astype(int) % 12 + 1
    return jahr, monat
