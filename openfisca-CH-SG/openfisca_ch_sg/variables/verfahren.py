"""Datumsregeln: ab wann Beiträge ausgerichtet werden.

Jede Bestimmung ist eine eigene Variable:
- Art. 9 Abs. 2 Satz 1 KiBG: rückwirkend, wenn das Gesuch innert 30 Tagen
  seit Inanspruchnahme eingereicht wird
- Art. 9 Abs. 2 Satz 2 KiBG: sonst ab dem Zeitpunkt der Gesuchstellung
- Art. 25 Abs. 1 KiBV: Gesuche bis drei Monate nach Vollzugsbeginn rückwirkend
  ab Vollzugsbeginn
- Art. 6 KiBV: Teilnahme der Einrichtung ab dem ersten Tag des Folgemonats
  nach der Bestätigung

Teamentscheide: Das Gesuchsdatum ist der Tag, an dem das Gesuch abgegeben
wird, bei der Gemeinde oder durch Postaufgabe; nach Verwaltungsrecht wahrt die
Abgabe die Frist (A10). Im Monat des Beitragsbeginns geben die Eltern nur die
Stunden ab diesem Tag ein (A9). In Monaten vor dem Beitragsbeginn besteht kein
Anspruch.
"""

from datetime import date

from numpy import datetime64, maximum, timedelta64, where
from openfisca_core.periods import ETERNITY, MONTH
from openfisca_core.variables import Variable

from openfisca_ch_sg.entities import Household, Person
from openfisca_ch_sg.hilfsfunktionen import (
    DATUM_FEHLT,
    VOLLZUGSBEGINN,
    eingabefehler,
    plus_monate,
)

FEHLT = datetime64(DATUM_FEHLT)


class betreuungsbeginn(Variable):
    value_type = date
    default_value = DATUM_FEHLT
    entity = Person
    definition_period = ETERNITY
    label = "Datum der Inanspruchnahme des Betreuungsangebots (Pflichtangabe für jedes Kind)"
    reference = "Art. 9 Abs. 2 KiBG"


class kibg_gesuchsdatum(Variable):
    value_type = date
    default_value = DATUM_FEHLT
    entity = Person
    definition_period = ETERNITY
    label = (
        "Tag, an dem das Gesuch abgegeben wird (bei der zuständigen kommunalen "
        "Stelle oder durch Postaufgabe; Pflichtangabe für jedes Kind, Annahme A10)"
    )
    reference = ("Art. 9 Abs. 1 und 2 KiBG", "Art. 25 Abs. 1 KiBV (Entwurf)")


class kibg_gesuch_innert_frist(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = (
        "Das Gesuch wird innert 30 Tagen seit Inanspruchnahme des "
        "Betreuungsangebots eingereicht"
    )
    reference = "Art. 9 Abs. 2 KiBG"

    def formula_2028_08(person, period, parameters):
        tage = int(parameters(period).kibg.verfahren.frist_rueckwirkung_tage)
        beginn = person("betreuungsbeginn", period)
        gesuch = person("kibg_gesuchsdatum", period)
        # A7: Die Frist beginnt am Tag nach der Inanspruchnahme; letzter Tag
        # ist Betreuungsbeginn + 30 Tage. Ein Gesuch vor dem Betreuungsbeginn
        # ist immer rechtzeitig.
        return gesuch <= beginn + timedelta64(tage, "D")


class kibg_gesuch_in_uebergangsfrist(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Das Gesuch wird bis spätestens drei Monate nach Vollzugsbeginn eingereicht"
    reference = "Art. 25 Abs. 1 KiBV (Entwurf)"

    def formula_2028_08(person, period, parameters):
        monate = int(parameters(period).kibg.verfahren.uebergang_frist_monate)
        # A7: Die Frist endet am Tag mit derselben Zahl (2028-08-01 → 2028-11-01).
        fristende = datetime64(plus_monate(VOLLZUGSBEGINN, monate))
        return person("kibg_gesuchsdatum", period) <= fristende


class kibg_beitragsbeginn(Variable):
    value_type = date
    default_value = DATUM_FEHLT
    entity = Person
    definition_period = MONTH
    label = "Tag, ab dem die Beiträge ausgerichtet werden"
    reference = ("Art. 9 Abs. 2 KiBG", "Art. 25 Abs. 1 KiBV (Entwurf)")

    def formula_2028_08(person, period, parameters):
        ist_kind = person.has_role(Household.KIND)
        beginn = person("betreuungsbeginn", period)
        gesuch = person("kibg_gesuchsdatum", period)
        eingabefehler(
            person,
            ist_kind * (beginn == FEHLT),
            "betreuungsbeginn",
            "Der Betreuungsbeginn des Kindes fehlt. Ohne ihn lässt sich nicht "
            "bestimmen, ab wann Beiträge ausgerichtet werden (Art. 9 Abs. 2 "
            "KiBG); es wird kein Beitrag berechnet.",
        )
        eingabefehler(
            person,
            ist_kind * (gesuch == FEHLT),
            "kibg_gesuchsdatum",
            "Das Gesuchsdatum fehlt (Tag, an dem das Gesuch abgegeben wird). "
            "Ohne es lässt sich nicht bestimmen, ab wann Beiträge "
            "ausgerichtet werden (Art. 9 Abs. 2 KiBG, Art. 25 KiBV); es wird "
            "kein Beitrag berechnet.",
        )
        innert_frist = person("kibg_gesuch_innert_frist", period)
        uebergang = person("kibg_gesuch_in_uebergangsfrist", period)
        # Art. 9 Abs. 2 KiBG: Satz 1 rückwirkend ab Betreuungsbeginn, Satz 2
        # sonst ab dem Zeitpunkt der Gesuchstellung.
        nach_art_9 = where(innert_frist, beginn, gesuch)
        # Art. 25 Abs. 1 KiBV: rückwirkend ab Vollzugsbeginn, aber nicht vor
        # dem Betreuungsbeginn (ohne Betreuung keine Kosten).
        nach_art_25 = maximum(beginn, datetime64(VOLLZUGSBEGINN))
        return where(uebergang, nach_art_25, nach_art_9)


class kibg_beitragsbeginn_erreicht(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Der Beitragsbeginn liegt in diesem Monat oder früher"
    reference = ("Art. 9 Abs. 2 KiBG", "Art. 25 Abs. 1 KiBV (Entwurf)")

    def formula_2028_08(person, period, parameters):
        beitragsbeginn = person("kibg_beitragsbeginn", period)
        monatsanfang = datetime64(period.start.date)
        monatsende = datetime64(period.stop.date)
        # A9: Im Monat des Beitragsbeginns zählen nur die Tage ab diesem Tag.
        # Mehr Betreuungstage, als ab dann im Monat bleiben, sind unmöglich.
        im_monat = (beitragsbeginn > monatsanfang) * (beitragsbeginn <= monatsende)
        verbleibende_tage = (monatsende - beitragsbeginn).astype(int) + 1
        tage = person("betreuungstage_mit_obhut", period)
        eingabefehler(
            person,
            im_monat * (tage > verbleibende_tage),
            "betreuungstage_mit_obhut",
            "Die Beiträge beginnen in diesem Monat erst am Beitragsbeginn. Es "
            "dürfen nur die Betreuungstage und -stunden ab diesem Tag angegeben "
            "werden (Art. 9 Abs. 2 KiBG, Annahme A9).",
        )
        return beitragsbeginn <= monatsende


class kibg_einrichtung_bestaetigt_am(Variable):
    value_type = date
    default_value = DATUM_FEHLT
    entity = Person
    definition_period = ETERNITY
    label = (
        "Tag, an dem das Amt für Soziales die Teilnahme der Einrichtung bestätigt "
        "hat (freiwillige Angabe; ohne sie gilt kibg_einrichtung_angemeldet)"
    )
    reference = ("Art. 5 KiBV (Entwurf)", "Art. 6 KiBV (Entwurf)")


class kibg_einrichtung_teilnahmebeginn(Variable):
    value_type = date
    default_value = DATUM_FEHLT
    entity = Person
    definition_period = MONTH
    label = "Erster Tag der Teilnahme der Einrichtung"
    reference = "Art. 6 KiBV (Entwurf)"

    def formula_2028_08(person, period, parameters):
        bestaetigt = person("kibg_einrichtung_bestaetigt_am", period)
        # Art. 6 KiBV: «am ersten Tag des Folgemonats, nachdem das Amt für
        # Soziales diese bestätigt hat».
        folgemonat = (bestaetigt.astype("datetime64[M]") + 1).astype("datetime64[D]")
        return where(bestaetigt == FEHLT, FEHLT, folgemonat)
