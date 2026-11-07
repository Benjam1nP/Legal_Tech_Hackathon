"""Massgebendes Einkommen und Vermögen (Art. 5 KiBG, Art. 8 bis 11 und 15 KiBV)."""

from numpy import abs as betrag, clip, logical_not as not_, where
from openfisca_core.periods import MONTH, YEAR
from openfisca_core.variables import Variable

from openfisca_ch_sg.entities import Household
from openfisca_ch_sg.hilfsfunktionen import mindestens


class kibg_antrag_aktuelle_gegebenheiten(Variable):
    value_type = bool
    entity = Household
    definition_period = YEAR
    label = "Antrag auf Bemessung nach aktuellen Gegebenheiten"
    reference = ("Art. 5 Abs. 4 KiBG", "Art. 11 Abs. 1 KiBV (Entwurf)")


class kibg_massgebendes_einkommen(Variable):
    value_type = float
    entity = Household
    # Monatlich, weil sich der Haushalt (Partnerin, Partner) im Jahr ändern
    # kann. Die Einkommen selbst sind Jahreswerte.
    definition_period = MONTH
    label = "Massgebendes Einkommen und Vermögen des Haushalts"
    reference = (
        "Art. 5 Abs. 1 bis 4 KiBG",
        "Art. 8 Abs. 1 KiBV (Entwurf)",
        "Art. 11 Abs. 1 und 2 KiBV (Entwurf)",
    )

    def formula_2028_08(household, period, parameters):
        schwelle = parameters(period).kibg.einkommen.schwelle_abweichung
        jahr = period.this_year

        # Wessen Einkommen zählt (Art. 8 Abs. 1 KiBV):
        # a) die Erziehungsberechtigten im Haushalt;
        # b) bei getrenntem Haushalt zusätzlich die Partnerin oder der Partner,
        #    wenn die Lebensgemeinschaft gefestigt ist.
        partner_zaehlt = household("kibg_gefestigte_lebensgemeinschaft", period) * (
            not_(household("gemeinsamer_haushalt", period))
        )

        veranlagt = household.members("me_steuerveranlagung", jahr)
        aktuell = household.members("me_aktuell", jahr)
        # Ohne Angabe (-1) gilt für diese Person die Steuerveranlagung.
        aktuell = where(aktuell < 0, veranlagt, aktuell)

        eltern = Household.ERZIEHUNGSBERECHTIGT
        partner = Household.PARTNER
        me_veranlagt = (
            household.sum(veranlagt, role=eltern)
            + household.sum(veranlagt, role=partner) * partner_zaehlt
        )
        me_aktuell = (
            household.sum(aktuell, role=eltern)
            + household.sum(aktuell, role=partner) * partner_zaehlt
        )

        # Aktuelle Gegebenheiten nur auf Antrag und ab 25 % Abweichung, in beide
        # Richtungen (Art. 11 Abs. 1 und 2 KiBV, O12). Verglichen wird das
        # Einkommen des Haushalts.
        antrag = household("kibg_antrag_aktuelle_gegebenheiten", jahr)
        abweichung = betrag(me_aktuell - me_veranlagt)
        wesentlich = mindestens(abweichung, schwelle * me_veranlagt)
        return where(antrag * wesentlich, me_aktuell, me_veranlagt)


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
        # → höchstens 1. Art. 15 Abs. 2 KiBV: «über Fr. 154'000.– erhalten
        # keinen Beitrag» → mindestens 0. Auslegung O4: Das gilt für den
        # Mindestbeitrag; Z2 der Gemeinde kommt in der Formel nach dem Faktor
        # und wird auch darüber ausgerichtet.
        return clip(faktor, 0, 1)
