"""Massgebendes Einkommen und Vermögen (Art. 5 KiBG, Art. 8 bis 11 und 15 KiBV).

Jede Bestimmung ist eine eigene Variable:
- Art. 8 Abs. 1 lit. a und lit. b KiBV: wessen Einkommen zählt
- Art. 5 Abs. 3 KiBG: Einkommen gemäss Steuerveranlagung
- Art. 5 Abs. 4 KiBG: Einkommen nach aktuellen Gegebenheiten
- Art. 11 Abs. 2 KiBV: Abweichung von wenigstens 25 Prozent
- Art. 11 Abs. 1 KiBV: aktuelle Gegebenheiten nur auf Antrag
- Art. 15 Abs. 1 und 2 KiBV: Begrenzung des Faktors
"""

from numpy import abs as betrag, logical_not as not_, maximum, minimum, where
from openfisca_core.periods import MONTH, YEAR
from openfisca_core.variables import Variable

from openfisca_ch_sg.entities import Household, Person
from openfisca_ch_sg.hilfsfunktionen import mindestens


class kibg_antrag_aktuelle_gegebenheiten(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Antrag auf Bemessung nach aktuellen Gegebenheiten"
    reference = ("Art. 5 Abs. 4 KiBG", "Art. 11 Abs. 1 KiBV (Entwurf)")


class kibg_einkommen_zaehlt_lit_a(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = (
        "Art. 8 Abs. 1 lit. a KiBV: bei gemeinsamem Haushalt der "
        "Erziehungsberechtigten zählt das Einkommen beider Erziehungsberechtigter"
    )
    reference = "Art. 8 Abs. 1 lit. a KiBV (Entwurf)"

    def formula_2028_08(person, period, parameters):
        ist_erziehungsberechtigt = person.has_role(Household.ERZIEHUNGSBERECHTIGT)
        gemeinsam = person.household("gemeinsamer_haushalt", period)
        return ist_erziehungsberechtigt * gemeinsam


class kibg_einkommen_zaehlt_lit_b(Variable):
    value_type = bool
    entity = Person
    definition_period = MONTH
    label = (
        "Art. 8 Abs. 1 lit. b KiBV: bei getrenntem Haushalt zählt das Einkommen "
        "der antragstellenden erziehungsberechtigten Person und der Partnerin "
        "oder des Partners in gefestigter Lebensgemeinschaft"
    )
    reference = ("Art. 8 Abs. 1 lit. b KiBV (Entwurf)", "Art. 8 Abs. 2 KiBV (Entwurf)")

    def formula_2028_08(person, period, parameters):
        getrennt = not_(person.household("gemeinsamer_haushalt", period))
        antragstellend = person("kibg_gesuchsteller", period)
        ist_partner = person.has_role(Household.PARTNER)
        gefestigt = person.household("kibg_gefestigte_lebensgemeinschaft", period)
        return getrennt * (antragstellend + ist_partner * gefestigt)


class kibg_me_steuerveranlagung_haushalt(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Massgebendes Einkommen und Vermögen gemäss letzter Steuerveranlagung"
    reference = ("Art. 5 Abs. 3 KiBG", "Art. 8 Abs. 1 KiBV (Entwurf)")

    def formula_2028_08(household, period, parameters):
        lit_a = household.members("kibg_einkommen_zaehlt_lit_a", period)
        lit_b = household.members("kibg_einkommen_zaehlt_lit_b", period)
        einkommen = household.members("me_steuerveranlagung", period.this_year)
        return household.sum(einkommen * (lit_a + lit_b))


class kibg_me_aktuell_haushalt(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Massgebendes Einkommen und Vermögen aufgrund aktueller Gegebenheiten"
    reference = ("Art. 5 Abs. 4 KiBG", "Art. 8 Abs. 1 KiBV (Entwurf)")

    def formula_2028_08(household, period, parameters):
        lit_a = household.members("kibg_einkommen_zaehlt_lit_a", period)
        lit_b = household.members("kibg_einkommen_zaehlt_lit_b", period)
        veranlagt = household.members("me_steuerveranlagung", period.this_year)
        aktuell = household.members("me_aktuell", period.this_year)
        # Ohne Angabe (-1) gilt für diese Person die Steuerveranlagung.
        aktuell = where(aktuell < 0, veranlagt, aktuell)
        return household.sum(aktuell * (lit_a + lit_b))


class kibg_abweichung_wesentlich(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = (
        "Die Abweichung beträgt zum Zeitpunkt der Gesuchstellung wenigstens "
        "25 Prozent des massgebenden Einkommens und Vermögens"
    )
    reference = "Art. 11 Abs. 2 KiBV (Entwurf)"

    def formula_2028_08(household, period, parameters):
        # Der Rechner schätzt den Monat der Gesuchstellung; me_aktuell ist der
        # Wert zu diesem Zeitpunkt. Die Neubestimmung während einer laufenden
        # Verfügung (Art. 11 Abs. 3 KiBV) ist nicht umgesetzt (README).
        # Abweichung in beide Richtungen (Entscheid O12). Gemessen wird am
        # massgebenden Einkommen nach Art. 8 Abs. 1 KiBV: bei gemeinsamem
        # Haushalt am Einkommen beider Eltern zusammen (lit. a). Bei getrenntem
        # Haushalt nur am Einkommen der gesuchstellenden Person, nicht an dem
        # des anderen Elternteils (lit. b). Lebt die gesuchstellende Person mit
        # einer neuen Partnerin oder einem neuen Partner in gefestigter
        # Lebensgemeinschaft, die oder der nicht erziehungsberechtigt ist,
        # zählt deren Einkommen nach lit. b mit (P7).
        schwelle = parameters(period).kibg.einkommen.schwelle_abweichung
        veranlagt = household("kibg_me_steuerveranlagung_haushalt", period)
        aktuell = household("kibg_me_aktuell_haushalt", period)
        return mindestens(betrag(aktuell - veranlagt), schwelle * veranlagt)


class kibg_massgebendes_einkommen(Variable):
    value_type = float
    entity = Household
    # Monatlich, weil sich der Haushalt (Partnerin, Partner) im Jahr ändern
    # kann. Die Einkommen selbst sind Jahreswerte.
    definition_period = MONTH
    label = "Massgebendes Einkommen und Vermögen des Haushalts"
    reference = ("Art. 5 Abs. 2 bis 4 KiBG", "Art. 11 Abs. 1 KiBV (Entwurf)")

    def formula_2028_08(household, period, parameters):
        # Art. 5 Abs. 3 KiBG: in der Regel die letzte Steuerveranlagung.
        # Art. 5 Abs. 4 KiBG und Art. 11 Abs. 1 KiBV: aktuelle Gegebenheiten
        # auf Antrag, wenn sich das Einkommen wesentlich verändert hat.
        antrag = household("kibg_antrag_aktuelle_gegebenheiten", period.this_year)
        wesentlich = household("kibg_abweichung_wesentlich", period)
        veranlagt = household("kibg_me_steuerveranlagung_haushalt", period)
        aktuell = household("kibg_me_aktuell_haushalt", period)
        return where(antrag * wesentlich, aktuell, veranlagt)


class kibg_einkommensfaktor(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Anteil des Höchstbeitrags je nach Einkommen (1 = voller Beitrag)"
    reference = ("Art. 13 und Anhang KiBV (Entwurf)", "Art. 15 KiBV (Entwurf)")

    def formula_2028_08(household, period, parameters):
        p = parameters(period).kibg.einkommen
        me = household("kibg_massgebendes_einkommen", period)
        # Klammerausdruck der Formel im Anhang: 1 − (ME − MinmE) / (MaxmE − MinmE)
        faktor = 1 - (me - p.min) / (p.max - p.min)
        # Art. 15 Abs. 1 KiBV: «bis Fr. 40'000.– erhalten den maximalen Beitrag»
        faktor = minimum(faktor, 1)
        # Art. 15 Abs. 2 KiBV: «über Fr. 154'000.– erhalten keinen Beitrag».
        # Auslegung O4: Das gilt für den Mindestbeitrag; Z2 der Gemeinde kommt
        # in der Formel nach dem Faktor und wird auch darüber ausgerichtet.
        faktor = maximum(faktor, 0)
        return faktor
