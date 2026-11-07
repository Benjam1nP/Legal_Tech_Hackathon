"""Höhe des Beitrags (Art. 6, 18 und 20 KiBG; Art. 13 bis 15, 24 und Anhang KiBV).

Formel im Anhang der KiBV, je Kind und Betreuungsstunde:
    B = (MaxV + Z1) × F + Z2
mit dem Einkommensfaktor F (kibg_einkommensfaktor). B wird aufgeteilt in den
Mindestbeitrag MaxV × F (Kanton und Gemeinde je hälftig, Art. 18 KiBG) und den
Zusatzbeitrag Z1 × F + Z2 (nur Gemeinde, Art. 20 Abs. 2 KiBG).
"""

from numpy import maximum, minimum, select
from openfisca_core.indexed_enums import Enum
from openfisca_core.periods import MONTH
from openfisca_core.variables import Variable

from openfisca_ch_sg.entities import Household, Person
from openfisca_ch_sg.hilfsfunktionen import auf_rappen_runden
from openfisca_ch_sg.variables.betreuung import KibgEinrichtungstyp


class KibgAltersstufe(Enum):
    unter_18_monate = "Unter 18 Monaten"
    ab_18_monate = "Ab 18 Monaten bis zur Einschulung"
    eingeschult = "Eingeschult bis zum Ende der Primarstufe"


class kibg_altersstufe(Variable):
    value_type = Enum
    possible_values = KibgAltersstufe
    default_value = KibgAltersstufe.unter_18_monate
    entity = Person
    definition_period = MONTH
    label = "Altersstufe für den Höchstbeitrag"
    reference = "Art. 14 Abs. 1 bis 3 KiBV (Entwurf)"

    def formula_2028_08(person, period, parameters):
        # Der höhere Ansatz gilt die vollen ersten 18 Lebensmonate (O2).
        altersgrenze = parameters(period).kibg.hoechstbeitrag.altersgrenze_monate
        eingeschult = person("eingeschult", period)
        unter_18 = person("kibg_alter_monate", period) < altersgrenze
        return select(
            [eingeschult, unter_18],
            [KibgAltersstufe.eingeschult, KibgAltersstufe.unter_18_monate],
            KibgAltersstufe.ab_18_monate,
        )


class kibg_hoechstbeitrag(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Höchster Beitrag je Betreuungsstunde (MaxV)"
    reference = "Art. 14 Abs. 1 bis 3 KiBV (Entwurf)"

    def formula_2028_08(person, period, parameters):
        p = parameters(period).kibg.hoechstbeitrag
        stufe = person("kibg_altersstufe", period)
        typ = person("kibg_einrichtungstyp", period)

        kita = typ == KibgEinrichtungstyp.kita
        tagesfamilie = typ == KibgEinrichtungstyp.tagesfamilie
        # Sonderschulen: Der Betrag richtet sich nach der Betreuungsform (O11),
        # hier schulergänzende Betreuung (Art. 3 Abs. 2 lit. d KiBG).
        schulergaenzend = (typ == KibgEinrichtungstyp.schulergaenzend) + (
            typ == KibgEinrichtungstyp.sonderschule
        )
        unter_18 = stufe == KibgAltersstufe.unter_18_monate
        ab_18 = stufe == KibgAltersstufe.ab_18_monate
        eingeschult = stufe == KibgAltersstufe.eingeschult

        # Für Kombinationen ohne Ansatz im Text (z. B. schulergänzende
        # Betreuung vor der Einschulung) gibt es keinen Beitrag.
        return select(
            [
                unter_18 * kita,
                unter_18 * tagesfamilie,
                ab_18 * kita,
                ab_18 * tagesfamilie,
                eingeschult * kita,
                eingeschult * schulergaenzend,
                eingeschult * tagesfamilie,
            ],
            [
                p.unter_18_monate.kita,
                p.unter_18_monate.tagesfamilie,
                p.ab_18_monate.kita,
                p.ab_18_monate.tagesfamilie,
                p.eingeschult.kita,
                p.eingeschult.schulergaenzend,
                p.eingeschult.tagesfamilie,
            ],
            0,
        )


class kibg_zusatzbeitrag_z1(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Einkommensabhängiger Zusatzbeitrag der Gemeinde je Stunde (Z1)"
    reference = ("Art. 20 Abs. 2 KiBG", "Art. 24 KiBV (Entwurf)")


class kibg_zusatzbeitrag_z2(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Einkommensunabhängiger Zusatzbeitrag der Gemeinde je Stunde (Z2)"
    reference = ("Art. 20 Abs. 2 KiBG", "Art. 24 KiBV (Entwurf)")


class kibg_beitrag_pro_stunde(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Beitrag je Betreuungsstunde (B), nicht gerundet"
    reference = "Art. 13 und Anhang KiBV (Entwurf)"

    def formula_2028_08(person, period, parameters):
        anspruch = person("kibg_anspruch", period)
        max_v = person("kibg_hoechstbeitrag", period)
        faktor = person.household("kibg_einkommensfaktor", period)
        z1 = person.household("kibg_zusatzbeitrag_z1", period)
        z2 = person.household("kibg_zusatzbeitrag_z2", period)
        return anspruch * ((max_v + z1) * faktor + z2)


class kibg_mindestbeitrag(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Mindestbeitrag im Monat (Kanton und Gemeinde)"
    reference = ("Art. 6 KiBG", "Art. 20 Abs. 1 KiBG")

    def formula_2028_08(person, period, parameters):
        rundung = parameters(period).kibg.rundung
        anspruch = person("kibg_anspruch", period)
        max_v = person("kibg_hoechstbeitrag", period)
        faktor = person.household("kibg_einkommensfaktor", period)
        stunden = person("kibg_subventionierte_stunden", period)
        kosten = person("kibg_betreuungskosten", period)
        beitrag = auf_rappen_runden(anspruch * max_v * faktor * stunden, rundung)
        # Höchstens die Kosten (Art. 6 Abs. 2 KiBG), nach dem Runden (A4).
        return minimum(beitrag, kosten)


class kibg_zusatzbeitrag(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Zusatzbeitrag der Gemeinde im Monat"
    reference = ("Art. 20 Abs. 2 und 3 KiBG", "Art. 24 KiBV (Entwurf)")

    def formula_2028_08(person, period, parameters):
        rundung = parameters(period).kibg.rundung
        anspruch = person("kibg_anspruch", period)
        faktor = person.household("kibg_einkommensfaktor", period)
        z1 = person.household("kibg_zusatzbeitrag_z1", period)
        z2 = person.household("kibg_zusatzbeitrag_z2", period)
        stunden = person("kibg_subventionierte_stunden", period)
        kosten = person("kibg_betreuungskosten", period)
        mindestbeitrag = person("kibg_mindestbeitrag", period)
        beitrag = auf_rappen_runden(anspruch * (z1 * faktor + z2) * stunden, rundung)
        # Mindest- und Zusatzbeitrag zusammen höchstens die Kosten
        # (Art. 20 Abs. 3 KiBG); gekürzt wird der Zusatzbeitrag (A2).
        return minimum(beitrag, maximum(kosten - mindestbeitrag, 0))


class kibg_beitrag_total(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Beitrag total im Monat (Mindest- und Zusatzbeitrag)"
    reference = "Art. 20 Abs. 3 KiBG"

    def formula_2028_08(person, period, parameters):
        mindestbeitrag = person("kibg_mindestbeitrag", period)
        zusatzbeitrag = person("kibg_zusatzbeitrag", period)
        return mindestbeitrag + zusatzbeitrag


class kibg_restkosten_eltern(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Kosten, die den Erziehungsberechtigten nach Abzug des Beitrags bleiben"
    reference = "Art. 12 Abs. 2 KiBG"

    def formula(person, period, parameters):
        # Ohne Datum: Vor dem Vollzugsbeginn gibt es keinen Beitrag, die Eltern
        # tragen die vollen Kosten (szenarien.md, X10).
        kosten = person("kibg_betreuungskosten", period)
        return kosten - person("kibg_beitrag_total", period)


class kibg_anteil_kanton(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Anteil des Kantons am Beitrag"
    reference = "Art. 18 Abs. 1 KiBG"

    def formula_2028_08(person, period, parameters):
        p = parameters(period).kibg
        mindestbeitrag = person("kibg_mindestbeitrag", period)
        return auf_rappen_runden(
            mindestbeitrag * p.finanzierung.anteil_kanton, p.rundung
        )


class kibg_anteil_gemeinde(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = (
        "Anteil der Gemeinde am Beitrag (Rest des Mindestbeitrags und Zusatzbeitrag)"
    )
    reference = ("Art. 18 Abs. 1 KiBG", "Art. 20 Abs. 2 KiBG")

    def formula_2028_08(person, period, parameters):
        mindestbeitrag = person("kibg_mindestbeitrag", period)
        zusatzbeitrag = person("kibg_zusatzbeitrag", period)
        kanton = person("kibg_anteil_kanton", period)
        return mindestbeitrag - kanton + zusatzbeitrag
