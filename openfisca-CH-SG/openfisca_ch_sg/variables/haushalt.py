"""Angaben zum Haushalt und zur Lebensgemeinschaft."""

from datetime import date

from openfisca_core.periods import ETERNITY, MONTH
from openfisca_core.variables import Variable

from openfisca_ch_sg.entities import Household
from openfisca_ch_sg.hilfsfunktionen import volle_jahre_seit


class gemeinsamer_haushalt(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = "Die Erziehungsberechtigten führen einen gemeinsamen Haushalt"
    reference = ("Art. 4 Abs. 1 lit. b KiBG", "Art. 8 Abs. 1 KiBV (Entwurf)")


class wohngemeinde(Variable):
    value_type = str
    entity = Household
    definition_period = MONTH
    label = "Politische Gemeinde der gesuchstellenden Person"
    reference = "Art. 2 KiBV (Entwurf)"


class verheiratet_oder_eingetragen(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = "Ehe oder eingetragene Partnerschaft mit der Partnerin oder dem Partner"
    reference = "Art. 8 Abs. 2 lit. a KiBV (Entwurf)"


class beginn_gemeinsamer_haushalt(Variable):
    value_type = date
    # Ohne Angabe gilt der gemeinsame Haushalt als nie begonnen.
    default_value = date(9999, 12, 31)
    entity = Household
    definition_period = ETERNITY
    label = "Beginn des gemeinsamen Haushalts mit der Partnerin oder dem Partner"
    reference = "Art. 8 Abs. 2 lit. b KiBV (Entwurf)"


class kibg_gefestigte_lebensgemeinschaft(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = "Gefestigte Lebensgemeinschaft mit der Partnerin oder dem Partner"
    reference = "Art. 8 Abs. 2 KiBV (Entwurf)"

    def formula_2028_08(household, period, parameters):
        mindestdauer_jahre = parameters(
            period
        ).kibg.einkommen.mindestdauer_konkubinat_jahre
        verheiratet = household("verheiratet_oder_eingetragen", period)
        beginn = household("beginn_gemeinsamer_haushalt", period)
        konkubinat = volle_jahre_seit(beginn, period) >= mindestdauer_jahre
        return verheiratet + konkubinat
