"""Anspruchsberechtigung (Art. 4 KiBG): jede Bedingung als eigene Variable."""

from numpy import logical_not as not_
from openfisca_core.indexed_enums import Enum
from openfisca_core.periods import MONTH
from openfisca_core.variables import Variable

from openfisca_ch_sg.entities import Household, Person
from openfisca_ch_sg.hilfsfunktionen import mindestens


class kibg_wohnsitz_erfuellt(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = "Die gesuchstellende Person wohnt im Kanton St. Gallen"
    reference = "Art. 4 Abs. 1 KiBG"

    def formula_2028_08(household, period, parameters):
        # Der Haushalt ist der Haushalt der gesuchstellenden Person (O8). Im
        # gemeinsamen Haushalt wohnen beide Erziehungsberechtigten am selben Ort.
        # Ohne erziehungsberechtigte Person gibt es keinen Anspruch («alle»
        # wäre bei null Personen sonst wahr).
        hat_eltern = household.nb_persons(Household.ERZIEHUNGSBERECHTIGT) > 0
        wohnsitz = household.members("wohnsitz_kanton_sg", period)
        alle_im_kanton = household.all(wohnsitz, role=Household.ERZIEHUNGSBERECHTIGT)
        return hat_eltern * alle_im_kanton


class kibg_beschaeftigung_erfuellt(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = "Der Mindest-Beschäftigungsgrad ist erreicht"
    reference = "Art. 4 Abs. 1 lit. a und b KiBG"

    def formula_2028_08(household, period, parameters):
        p = parameters(period).kibg.anspruch
        grad = household.members("beschaeftigungsgrad", period)
        # lit. a: jede erziehungsberechtigte Person mindestens 20 % (O3: kumulativ)
        jeder_genug = household.all(
            mindestens(grad, p.min_beschaeftigungsgrad),
            role=Household.ERZIEHUNGSBERECHTIGT,
        )
        # lit. b: im gemeinsamen Haushalt zusammen mindestens 120 %
        zusammen = household.sum(grad, role=Household.ERZIEHUNGSBERECHTIGT)
        zusammen_genug = mindestens(zusammen, p.min_beschaeftigungsgrad_gemeinsam)
        gemeinsam = household("gemeinsamer_haushalt", period)
        hat_eltern = household.nb_persons(Household.ERZIEHUNGSBERECHTIGT) > 0
        return hat_eltern * jeder_genug * (zusammen_genug + not_(gemeinsam))


class kibg_ausnahme_bewilligt(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = "Die Gemeinde hat vom Mindest-Beschäftigungsgrad entbunden"
    reference = ("Art. 4 Abs. 2 KiBG", "Art. 12 KiBV (Entwurf)")


class KibgAusnahmegrund(Enum):
    keiner = "Kein Ausnahmegrund"
    berufliche_integration = (
        "Berufliche Integration (Stellensuche, Aus- und Weiterbildung, Integration)"
    )
    familiaere_belastung = "Familiäre Belastung (Gesundheit, Überforderung)"
    indikation_kind = "Entwicklungs- oder Verhaltensauffälligkeit oder sprachliche Indikation des Kindes"


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
    reference = ("Art. 3 und 4 KiBG", "Art. 7 KiBV (Entwurf)")

    def formula_2028_08(person, period, parameters):
        wohnsitz = person.household("kibg_wohnsitz_erfuellt", period)
        beschaeftigung = person.household("kibg_beschaeftigung_erfuellt", period)
        ausnahme = person.household("kibg_ausnahme_bewilligt", period)
        alter = person("kibg_alter_erfuellt", period)
        einrichtung = person("kibg_einrichtung_berechtigt", period)
        return wohnsitz * (beschaeftigung + ausnahme) * alter * einrichtung
