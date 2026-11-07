"""Höhe des Beitrags (Art. 6, 18 und 20 KiBG; Art. 13 bis 15, 24 und Anhang KiBV).

Die Formel im Anhang der KiBV steht im Text einmal und deshalb auch im Code
einmal: `formel_anhang` in hilfsfunktionen.py. Sie wird dort angewendet, wo der
Text sie anwendet:

- B, Beitrag je Kind und Betreuungsstunde (Art. 13 und Anhang KiBV):
  Formel mit den Zusatzbeiträgen Z1 und Z2 der Gemeinde.
- Mindestbeitrag (Art. 6 und Art. 20 Abs. 1 KiBG): der Beitrag nach dem
  linearen Modell ohne Zusatzbeiträge, also dieselbe Formel mit Z1 = Z2 = 0.
  Kanton und Gemeinde tragen ihn je hälftig (Art. 18 Abs. 1 KiBG).
- Zusatzbeitrag (Art. 20 Abs. 2 KiBG): was die Gemeinde «über ihren
  Kostenanteil hinaus» aufstockt, also B minus Mindestbeitrag.
"""

from numpy import minimum, select
from openfisca_core.indexed_enums import Enum
from openfisca_core.periods import MONTH
from openfisca_core.variables import Variable

from openfisca_ch_sg.entities import Household, Person
from openfisca_ch_sg.hilfsfunktionen import auf_rappen_runden, formel_anhang
from openfisca_ch_sg.variables.betreuung import KibgEinrichtungstyp


class KibgAltersstufe(Enum):
    unter_18_monate = "Unter 18 Monaten"
    ueber_18_monate = "Über 18 Monaten bis zur Einschulung"
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
        # «unter 18 Monaten» (Abs. 1) gilt die vollen ersten 18 Lebensmonate;
        # «über 18 Monaten» (Abs. 2) ab dem 18-Monate-Geburtstag (Entscheid O2).
        altersgrenze = parameters(period).kibg.hoechstbeitrag.altersgrenze_monate
        eingeschult = person("eingeschult", period)
        unter_18 = person("kibg_alter_monate", period) < altersgrenze
        return select(
            [eingeschult, unter_18],
            [KibgAltersstufe.eingeschult, KibgAltersstufe.unter_18_monate],
            KibgAltersstufe.ueber_18_monate,
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
        ueber_18 = stufe == KibgAltersstufe.ueber_18_monate
        eingeschult = stufe == KibgAltersstufe.eingeschult

        # Für Kombinationen ohne Ansatz in Art. 14 KiBV (z. B. schulergänzende
        # Betreuung vor der Einschulung) ist der Höchstbeitrag 0: Der Anspruch
        # kann erfüllt sein, der Beitrag ist trotzdem Fr. 0. Das Interface
        # erklärt diesen Fall (docs/output-konzept.md).
        return select(
            [
                unter_18 * kita,
                unter_18 * tagesfamilie,
                ueber_18 * kita,
                ueber_18 * tagesfamilie,
                eingeschult * kita,
                eingeschult * schulergaenzend,
                eingeschult * tagesfamilie,
            ],
            [
                p.unter_18_monate.kita,
                p.unter_18_monate.tagesfamilie,
                p.ueber_18_monate.kita,
                p.ueber_18_monate.tagesfamilie,
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
    label = "Beitrag je Kind und Betreuungsstunde (B), nicht gerundet"
    reference = ("Art. 13 KiBV (Entwurf)", "Anhang KiBV (Entwurf)")

    def formula_2028_08(person, period, parameters):
        anspruch = person("kibg_anspruch", period)
        max_v = person("kibg_hoechstbeitrag", period)
        faktor = person.household("kibg_einkommensfaktor", period)
        z1 = person.household("kibg_zusatzbeitrag_z1", period)
        z2 = person.household("kibg_zusatzbeitrag_z2", period)
        return anspruch * formel_anhang(max_v, z1, z2, faktor)


class kibg_mindestbeitrag_pro_stunde(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Mindestbeitrag je Kind und Betreuungsstunde (Formel ohne Zusatzbeiträge)"
    reference = (
        "Art. 6 Abs. 1 KiBG",
        "Art. 20 Abs. 1 KiBG",
        "Art. 13 KiBV (Entwurf)",
        "Anhang KiBV (Entwurf)",
    )

    def formula_2028_08(person, period, parameters):
        # Art. 20 Abs. 1 KiBG: Die Beiträge nach Art. 6 (lineares Modell) gelten
        # als Mindestbeiträge. Z1 und Z2 sind Zusatzbeiträge der Gemeinde
        # (Anhang, Art. 20 Abs. 2 KiBG) und gehören nicht dazu.
        anspruch = person("kibg_anspruch", period)
        max_v = person("kibg_hoechstbeitrag", period)
        faktor = person.household("kibg_einkommensfaktor", period)
        return anspruch * formel_anhang(max_v, 0, 0, faktor)


class kibg_zusatzbeitrag_pro_stunde(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Zusatzbeitrag der Gemeinde je Kind und Betreuungsstunde"
    reference = ("Art. 20 Abs. 2 KiBG", "Art. 24 KiBV (Entwurf)")

    def formula_2028_08(person, period, parameters):
        # Art. 20 Abs. 2 KiBG: Die Gemeinde stockt die Mindestbeiträge «über
        # ihren Kostenanteil hinaus» auf. Der Zusatzbeitrag ist der Teil von B,
        # der über den Mindestbeitrag hinausgeht.
        beitrag = person("kibg_beitrag_pro_stunde", period)
        mindestbeitrag = person("kibg_mindestbeitrag_pro_stunde", period)
        return beitrag - mindestbeitrag


class kibg_mindestbeitrag(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Mindestbeitrag im Monat (Kanton und Gemeinde je hälftig)"
    reference = (
        "Art. 6 Abs. 1 und 2 KiBG",
        "Art. 20 Abs. 1 KiBG",
        "Art. 14 Abs. 4 KiBV (Entwurf)",
    )

    def formula_2028_08(person, period, parameters):
        rundung = parameters(period).kibg.rundung
        je_stunde = person("kibg_mindestbeitrag_pro_stunde", period)
        stunden = person("kibg_subventionierte_stunden", period)
        kosten = person("kibg_betreuungskosten", period)
        beitrag = auf_rappen_runden(je_stunde * stunden, rundung)
        # Art. 6 Abs. 2 KiBG: «Ein Beitrag darf die Kosten ... nicht
        # übersteigen.» Begrenzt nach dem Runden (A4).
        return minimum(beitrag, kosten)


class kibg_beitrag_total(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Beitrag total im Monat (Mindest- und Zusatzbeitrag)"
    reference = "Art. 20 Abs. 3 KiBG"

    def formula_2028_08(person, period, parameters):
        rundung = parameters(period).kibg.rundung
        mindestbeitrag = person("kibg_mindestbeitrag", period)
        je_stunde = person("kibg_zusatzbeitrag_pro_stunde", period)
        stunden = person("kibg_subventionierte_stunden", period)
        kosten = person("kibg_betreuungskosten", period)
        zusatzbeitrag = auf_rappen_runden(je_stunde * stunden, rundung)
        # Art. 20 Abs. 3 KiBG: «Die Summe aus einem Mindestbeitrag und einem
        # allfälligen Zusatzbeitrag darf die Kosten ... nicht übersteigen.»
        # (Der Mindestbeitrag allein ist schon nach Art. 6 Abs. 2 KiBG begrenzt.)
        return minimum(mindestbeitrag + zusatzbeitrag, kosten)


class kibg_zusatzbeitrag(Variable):
    value_type = float
    entity = Person
    definition_period = MONTH
    label = "Zusatzbeitrag der Gemeinde im Monat"
    reference = ("Art. 20 Abs. 2 und 3 KiBG", "Art. 24 KiBV (Entwurf)")

    def formula_2028_08(person, period, parameters):
        # Was nach Art. 20 Abs. 3 KiBG über dem Mindestbeitrag bleibt: Muss
        # gekürzt werden, wird zuerst der Zusatzbeitrag gekürzt (Annahme A2).
        beitrag_total = person("kibg_beitrag_total", period)
        mindestbeitrag = person("kibg_mindestbeitrag", period)
        return beitrag_total - mindestbeitrag


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
