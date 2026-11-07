"""Angaben zur Betreuung des Kindes: Einrichtung, Stunden, Kosten."""

from numpy import minimum
from openfisca_core.indexed_enums import Enum
from openfisca_core.periods import MONTH
from openfisca_core.variables import Variable

from openfisca_ch_sg.entities import Person


class KibgEinrichtungstyp(Enum):
    keine = "Keine anerkannte Einrichtung"
    kita = "Kindertagesstätte"
    tagesfamilie = "Tagesfamilie (über eine Tagesfamilienorganisation)"
    schulergaenzend = "Einrichtung für schulergänzende Betreuung"
    sonderschule = "Schulergänzende Betreuung einer anerkannten privaten Sonderschule"


class kibg_einrichtungstyp(Variable):
    value_type = Enum
    possible_values = KibgEinrichtungstyp
    default_value = KibgEinrichtungstyp.keine
    entity = Person
    definition_period = MONTH
    label = "Art der Einrichtung, in der das Kind betreut wird"
    reference = "Art. 3 Abs. 2 KiBG"


class kibg_einrichtung_anerkannt(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Die Einrichtung ist anerkannt"
    reference = "Art. 3 Abs. 2 KiBG"


class kibg_einrichtung_angemeldet(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Die Einrichtung ist bei der kantonalen Stelle angemeldet"
    reference = "Art. 3 Abs. 3 KiBG"


class kibg_einrichtung_berechtigt(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Betreuung in einer anerkannten und angemeldeten Einrichtung"
    reference = "Art. 3 Abs. 1 KiBG"

    def formula_2028_08(person, period, parameters):
        typ = person("kibg_einrichtungstyp", period)
        anerkannt = person("kibg_einrichtung_anerkannt", period)
        angemeldet = person("kibg_einrichtung_angemeldet", period)
        return (typ != KibgEinrichtungstyp.keine) * anerkannt * angemeldet


class eingeschult(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = (
        "Das Kind ist eingeschult, d. h. ab Eintritt in den obligatorischen "
        "Kindergarten (Annahme A8)"
    )
    reference = ("Art. 14 Abs. 2 und 3 KiBV (Entwurf)", "Art. 16 Abs. 1 KiBV (Entwurf)")


class primarschule_abgeschlossen(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Das Kind hat die Primarschule abgeschlossen"
    reference = "Art. 4 Abs. 3 KiBG"


class betreuungsstunden(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Betreuungsstunden im Monat (nur Tage mit faktischer Obhut)"
    reference = ("Art. 7 KiBV (Entwurf)", "Art. 14 Abs. 4 KiBV (Entwurf)")


class betreuungstage_mit_obhut(Variable):
    value_type = int
    entity = Person
    definition_period = MONTH
    label = "Betreuungstage im Monat mit faktischer Obhut"
    reference = ("Art. 7 KiBV (Entwurf)", "Art. 14 Abs. 4 KiBV (Entwurf)")


class kibg_betreuungskosten(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Kosten der Erziehungsberechtigten für die Betreuung im Monat"
    reference = "Art. 6 Abs. 2 KiBG"


class kibg_subventionierte_stunden(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Subventionierte Betreuungsstunden im Monat"
    reference = "Art. 14 Abs. 4 KiBV (Entwurf)"

    def formula_2028_08(person, period, parameters):
        # Höchstens 12 Stunden je Betreuungstag. Die Grenze von 5 Tagen pro
        # Woche wird nicht angewendet, weil die Eingaben Monatswerte sind (A3).
        max_stunden_pro_tag = parameters(period).kibg.betreuung.max_stunden_pro_tag
        stunden = person("betreuungsstunden", period)
        tage = person("betreuungstage_mit_obhut", period)
        return minimum(stunden, tage * max_stunden_pro_tag)
