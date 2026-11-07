"""Kleine Hilfsfunktionen, die mehrere Formeln brauchen."""

from numpy import floor, round as runden


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
