"""Angaben zu den Personen: Alter, Wohnsitz, Pensum, Einkommen."""

from datetime import date

from openfisca_core.indexed_enums import Enum
from openfisca_core.periods import ETERNITY, MONTH, YEAR
from openfisca_core.variables import Variable

from openfisca_ch_sg.entities import Household, Person
from openfisca_ch_sg.hilfsfunktionen import (
    GEBURTSDATUM_FEHLT,
    eingabefehler,
    monate_seit,
)


class geburtsdatum(Variable):
    value_type = date
    # Kein Ersatzwert: Fehlt das Geburtsdatum eines Kindes, wird nicht
    # gerechnet (kibg_alter_monate).
    default_value = GEBURTSDATUM_FEHLT
    entity = Person
    definition_period = ETERNITY
    label = "Geburtsdatum (Pflichtangabe für jedes Kind)"
    reference = ("Art. 4 Abs. 3 KiBG", "Art. 14 Abs. 1 und 2 KiBV (Entwurf)")


class kibg_alter_monate(Variable):
    value_type = int
    entity = Person
    definition_period = MONTH
    label = "Alter in vollen Monaten am ersten Tag des Monats"
    reference = ("Art. 4 Abs. 3 KiBG", "Art. 14 Abs. 1 und 2 KiBV (Entwurf)")

    def formula(person, period, parameters):
        geburtsdatum = person("geburtsdatum", period)
        # Ohne Geburtsdatum lassen sich weder das Mindestalter (Art. 4 Abs. 3
        # KiBG) noch der Höchstbeitrag (Art. 14 KiBV) bestimmen: kein Beitrag,
        # sondern ein Fehler.
        eingabefehler(
            person,
            (geburtsdatum == GEBURTSDATUM_FEHLT) * person.has_role(Household.KIND),
            "geburtsdatum",
            "Geburtsdatum des Kindes fehlt. Ohne Geburtsdatum können das "
            "Mindestalter (Art. 4 Abs. 3 KiBG) und der Höchstbeitrag "
            "(Art. 14 KiBV, Entwurf) nicht bestimmt werden; es wird kein "
            "Beitrag berechnet.",
        )
        return monate_seit(geburtsdatum, period)


class wohnsitz_kanton_sg(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = "Zivilrechtlicher Wohnsitz im Kanton St. Gallen"
    reference = "Art. 4 Abs. 1 KiBG"


class kibg_gesuchstellend(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = (
        "Diese erziehungsberechtigte Person stellt das Gesuch (Pflichtangabe, "
        "wenn zwei Erziehungsberechtigte im Haushalt sind)"
    )
    reference = ("Art. 9 Abs. 1 KiBG", "Art. 8 Abs. 1 lit. b KiBV (Entwurf)")


class beschaeftigungsgrad(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Beschäftigungsgrad als Anteil (0.8 = 80 %)"
    reference = "Art. 4 Abs. 1 KiBG"


class me_steuerveranlagung(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    label = "Massgebendes Einkommen und Vermögen gemäss letzter Steuerveranlagung"
    reference = ("Art. 5 Abs. 3 KiBG", "Art. 9 KiBV (Entwurf)")


class me_aktuell(Variable):
    value_type = float
    # -1 heisst «nicht angegeben»: dann gilt die Steuerveranlagung.
    default_value = -1
    entity = Person
    definition_period = YEAR
    label = "Massgebendes Einkommen und Vermögen nach aktuellen Gegebenheiten"
    reference = ("Art. 5 Abs. 4 KiBG", "Art. 11 KiBV (Entwurf)")


class Besteuerungsart(Enum):
    ordentlich = "Ordentlich besteuert"
    quellenbesteuert = "Quellenbesteuert"
    ohne_veranlagung = "Keine rechtskräftige Steuerveranlagung"


class besteuerungsart(Variable):
    value_type = Enum
    possible_values = Besteuerungsart
    default_value = Besteuerungsart.ordentlich
    entity = Person
    definition_period = YEAR
    label = "Besteuerungsart (nur zur Information, das Einkommen wird eingegeben)"
    reference = "Art. 10 Abs. 1 KiBV (Entwurf)"
