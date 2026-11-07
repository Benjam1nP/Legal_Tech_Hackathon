"""Anspruchsberechtigung (Art. 4 KiBG): jede Bedingung als eigene Variable."""

from numpy import logical_not as not_, where
from openfisca_core.indexed_enums import Enum
from openfisca_core.periods import MONTH
from openfisca_core.variables import Variable

from openfisca_ch_sg.entities import Household, Person
from openfisca_ch_sg.hilfsfunktionen import eingabefehler, mindestens


class kibg_gesuchsteller(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Gesuchstellende erziehungsberechtigte Person"
    reference = (
        "Art. 2 Abs. 1 KiBG",
        "Art. 9 Abs. 1 KiBG",
        "Art. 8 Abs. 1 lit. b KiBV (Entwurf)",
    )

    def formula_2028_08(person, period, parameters):
        eltern = Household.ERZIEHUNGSBERECHTIGT
        ist_erziehungsberechtigt = person.has_role(eltern)
        angegeben = person("kibg_gesuchstellend", period)
        anzahl_eltern = person.household.nb_persons(eltern)
        anzahl_angegeben = person.household.sum(
            angegeben * ist_erziehungsberechtigt, role=eltern
        )
        # Das Gesuch stellen die Erziehungsberechtigten (Art. 9 Abs. 1 KiBG).
        eingabefehler(
            person,
            angegeben * not_(ist_erziehungsberechtigt),
            "kibg_gesuchstellend",
            "Das Gesuch kann nur eine erziehungsberechtigte Person stellen "
            "(Art. 9 Abs. 1 KiBG).",
        )
        eingabefehler(
            person,
            ist_erziehungsberechtigt * (anzahl_angegeben > 1),
            "kibg_gesuchstellend",
            "Es kann nur eine Person als gesuchstellend angegeben werden.",
        )
        eingabefehler(
            person,
            ist_erziehungsberechtigt * (anzahl_eltern > 1) * (anzahl_angegeben == 0),
            "kibg_gesuchstellend",
            "Im Haushalt leben zwei Erziehungsberechtigte. Es muss angegeben "
            "werden, wer das Gesuch stellt, denn nur diese Person muss im "
            "Kanton wohnen (Art. 4 Abs. 1 KiBG, Entscheid O8).",
        )
        # Ist nur eine erziehungsberechtigte Person im Haushalt, stellt sie das
        # Gesuch (der Haushalt ist der Haushalt der gesuchstellenden Person).
        return ist_erziehungsberechtigt * (angegeben + (anzahl_eltern == 1))


class kibg_wohnsitz_erfuellt(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = "Die gesuchstellende Person hat zivilrechtlichen Wohnsitz im Kanton"
    reference = "Art. 4 Abs. 1 KiBG"

    def formula_2028_08(household, period, parameters):
        # «Erziehungsberechtigte mit zivilrechtlichem Wohnsitz im Kanton»:
        # massgebend ist nur die gesuchstellende Person (Entscheid O8). Ohne
        # erziehungsberechtigte Person im Haushalt ist das Ergebnis «nein».

        # Die Angabe «gemeinsamer Haushalt» muss zur Anzahl der
        # Erziehungsberechtigten passen. Erziehungsberechtigte sind nach
        # Art. 2 Abs. 1 KiBG die Personen, die Beiträge geltend machen: Bei
        # getrennten Eltern ist das nur die gesuchstellende Person. Geprüft
        # beim Haushalt, damit die Fehlermeldung auf das Feld des Haushalts
        # zeigt (households/.../gemeinsamer_haushalt).
        gemeinsam = household("gemeinsamer_haushalt", period)
        anzahl_eltern = household.nb_persons(Household.ERZIEHUNGSBERECHTIGT)
        eingabefehler(
            household,
            not_(gemeinsam) * (anzahl_eltern > 1),
            "gemeinsamer_haushalt",
            "Bei getrennten Eltern ist nur die gesuchstellende Person "
            "erziehungsberechtigt im Sinn von Art. 2 Abs. 1 KiBG. Der andere "
            "Elternteil wird nicht erfasst; er stellt allenfalls ein eigenes "
            "Gesuch für seine Betreuungstage.",
        )
        eingabefehler(
            household,
            gemeinsam * (anzahl_eltern == 1),
            "gemeinsamer_haushalt",
            "Ein gemeinsamer Haushalt der Erziehungsberechtigten "
            "(Art. 4 Abs. 1 lit. b KiBG, Art. 8 Abs. 1 lit. a KiBV, Entwurf) "
            "setzt zwei Erziehungsberechtigte im Haushalt voraus.",
        )

        gesuchsteller = household.members("kibg_gesuchsteller", period)
        wohnsitz = household.members("wohnsitz_kanton_sg", period)
        return household.any(
            gesuchsteller * wohnsitz, role=Household.ERZIEHUNGSBERECHTIGT
        )


class kibg_beschaeftigung_lit_a_erfuellt(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = (
        "Art. 4 Abs. 1 lit. a KiBG: jede erziehungsberechtigte Person wenigstens 20 %"
    )
    reference = "Art. 4 Abs. 1 lit. a KiBG"

    def formula_2028_08(household, period, parameters):
        p = parameters(period).kibg.anspruch
        grad = household.members("beschaeftigungsgrad", period)
        return household.all(
            mindestens(grad, p.min_beschaeftigungsgrad),
            role=Household.ERZIEHUNGSBERECHTIGT,
        )


class kibg_beschaeftigung_lit_b_erfuellt(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = (
        "Art. 4 Abs. 1 lit. b KiBG: zusammen wenigstens 120 %, wenn die "
        "Erziehungsberechtigten einen gemeinsamen Haushalt führen"
    )
    reference = "Art. 4 Abs. 1 lit. b KiBG"

    def formula_2028_08(household, period, parameters):
        p = parameters(period).kibg.anspruch
        grad = household.members("beschaeftigungsgrad", period)
        zusammen = household.sum(grad, role=Household.ERZIEHUNGSBERECHTIGT)
        zusammen_genug = mindestens(zusammen, p.min_beschaeftigungsgrad_gemeinsam)
        gemeinsam = household("gemeinsamer_haushalt", period)
        # lit. b gilt nur bei gemeinsamem Haushalt («wenn sie einen
        # gemeinsamen Haushalt führen»); sonst ist sie nicht anwendbar.
        return zusammen_genug + not_(gemeinsam)


class kibg_beschaeftigung_erfuellt(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = "Der Beschäftigungsgrad nach Art. 4 Abs. 1 lit. a und b KiBG ist erreicht"
    reference = "Art. 4 Abs. 1 lit. a und b KiBG"

    def formula_2028_08(household, period, parameters):
        # lit. a und lit. b gelten kumulativ (Entscheid O3).
        lit_a = household("kibg_beschaeftigung_lit_a_erfuellt", period)
        lit_b = household("kibg_beschaeftigung_lit_b_erfuellt", period)
        hat_eltern = household.nb_persons(Household.ERZIEHUNGSBERECHTIGT) > 0
        return hat_eltern * lit_a * lit_b


class kibg_ausnahme_bewilligt(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = "Die Gemeinde hat vom Mindest-Beschäftigungsgrad entbunden"
    reference = ("Art. 4 Abs. 2 KiBG", "Art. 12 KiBV (Entwurf)")


class KibgAusnahmegrund(Enum):
    keiner = "Kein Ausnahmegrund"
    # Wortlaut von Art. 12 Abs. 1 lit. a bis c KiBV (Entwurf)
    berufliche_integration = (
        "Berufliche Integration, namentlich Stellensuche, Aus- und Weiterbildung "
        "oder Integrationsmassnahmen für ausländische Staatsangehörige"
    )
    familiaere_belastung = (
        "Familiäre Belastungen wie gesundheitliche Beeinträchtigungen oder "
        "Überforderung der Erziehungsberechtigten"
    )
    indikation_kind = (
        "Entwicklungs- oder Verhaltensauffälligkeiten des Kindes oder eine "
        "sprachliche Indikation"
    )


class kibg_ausnahmegrund(Variable):
    value_type = Enum
    possible_values = KibgAusnahmegrund
    default_value = KibgAusnahmegrund.keiner
    entity = Household
    definition_period = MONTH
    label = "Grund für die Entbindung (nur zur Information; der Entscheid ist kibg_ausnahme_bewilligt)"
    reference = "Art. 12 KiBV (Entwurf)"


class kibg_alter_erfuellt(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Das Kind ist mindestens 3 Monate alt und hat die Primarschule nicht abgeschlossen"
    reference = "Art. 4 Abs. 3 KiBG"

    def formula_2028_08(person, period, parameters):
        mindestalter = parameters(period).kibg.anspruch.mindestalter_monate
        ist_kind = person.has_role(Household.KIND)
        alt_genug = person("kibg_alter_monate", period) >= mindestalter
        abgeschlossen = person("primarschule_abgeschlossen", period)
        return ist_kind * alt_genug * not_(abgeschlossen)


class kibg_anspruch(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Anspruch auf Beiträge für dieses Kind"
    reference = (
        "Art. 3 Abs. 1 KiBG",
        "Art. 4 Abs. 1 bis 3 KiBG",
        "Art. 9 Abs. 2 KiBG",
        "Art. 25 Abs. 1 KiBV (Entwurf)",
    )

    def formula_2028_08(person, period, parameters):
        wohnsitz = person.household("kibg_wohnsitz_erfuellt", period)
        beschaeftigung = person.household("kibg_beschaeftigung_erfuellt", period)
        ausnahme = person.household("kibg_ausnahme_bewilligt", period)
        alter = person("kibg_alter_erfuellt", period)
        einrichtung = person("kibg_einrichtung_berechtigt", period)
        # Art. 9 Abs. 2 KiBG und Art. 25 KiBV: vor dem Beitragsbeginn werden
        # keine Beiträge ausgerichtet (Teamentscheid: wirkt auf den Betrag).
        # Nur für Kinder geprüft, damit für Eltern keine Daten nötig sind.
        ist_kind = person.has_role(Household.KIND)
        beitragsbeginn = where(
            ist_kind, person("kibg_beitragsbeginn_erreicht", period), False
        )
        return (
            wohnsitz
            * (beschaeftigung + ausnahme)
            * alter
            * einrichtung
            * beitragsbeginn
        )
