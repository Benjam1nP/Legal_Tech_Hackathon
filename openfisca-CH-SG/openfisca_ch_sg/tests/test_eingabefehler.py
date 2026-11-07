"""Eingabefehler F1 bis F9 aus challenge/szenarien.md (Teil 3b).

Ohne diese Angaben kann der Text nicht angewendet werden. Die Berechnung muss
abbrechen, statt einen Betrag zu liefern. YAML-Tests können nur Werte prüfen,
deshalb stehen diese Fälle hier.
"""

import pytest
from openfisca_core.errors import SituationParsingError
from openfisca_core.simulation_builder import SimulationBuilder

from openfisca_ch_sg import CountryTaxBenefitSystem

SYSTEM = CountryTaxBenefitSystem()
MONAT = "2028-09"


def p1(mutter=None, vater=None, lina=None, partner=False, gemeinsam=True):
    """Familie P1 aus challenge/szenarien.md mit einzelnen Änderungen."""
    personen = {
        "mutter": {
            "wohnsitz_kanton_sg": {MONAT: True},
            "beschaeftigungsgrad": {MONAT: 1.0},
            "me_steuerveranlagung": {"2028": 60000},
            "kibg_gesuchstellend": {MONAT: True},
        },
        "vater": {
            "wohnsitz_kanton_sg": {MONAT: True},
            "beschaeftigungsgrad": {MONAT: 0.4},
            "me_steuerveranlagung": {"2028": 37000},
        },
        "lina": {
            "geburtsdatum": {"ETERNITY": "2027-09-01"},
            "kibg_einrichtungstyp": {MONAT: "kita"},
            "kibg_einrichtung_anerkannt": {MONAT: True},
            "kibg_einrichtung_angemeldet": {MONAT: True},
            "betreuungsstunden": {MONAT: 80},
            "betreuungstage_mit_obhut": {MONAT: 8},
            "kibg_betreuungskosten": {MONAT: 1040},
        },
    }
    for name, aenderung in (("mutter", mutter), ("vater", vater), ("lina", lina)):
        if aenderung is not None:
            personen[name] = aenderung(personen[name])
    haushalt = {
        "erziehungsberechtigte": ["mutter", "vater"],
        "kinder": ["lina"],
        "gemeinsamer_haushalt": {MONAT: gemeinsam},
    }
    if partner:
        personen["partnerin"] = {"kibg_gesuchstellend": {MONAT: True}}
        haushalt["partner"] = ["partnerin"]
    return SimulationBuilder().build_from_entities(
        SYSTEM, {"persons": personen, "households": {"familie": haushalt}}
    )


def ohne(schluessel):
    return lambda angaben: {k: v for k, v in angaben.items() if k != schluessel}


def test_p1_ohne_aenderung_rechnet():
    assert p1().calculate("kibg_beitrag_total", MONAT)[2] == pytest.approx(440)


def test_f1_kind_ohne_geburtsdatum():
    simulation = p1(lina=ohne("geburtsdatum"))
    with pytest.raises(SituationParsingError, match="Geburtsdatum des Kindes fehlt"):
        simulation.calculate("kibg_beitrag_total", MONAT)


def test_f2_zwei_erziehungsberechtigte_ohne_gesuchsteller():
    simulation = p1(mutter=ohne("kibg_gesuchstellend"))
    with pytest.raises(SituationParsingError, match="wer das Gesuch stellt"):
        simulation.calculate("kibg_beitrag_total", MONAT)


def test_f3_zwei_gesuchstellende_personen():
    simulation = p1(vater=lambda v: {**v, "kibg_gesuchstellend": {MONAT: True}})
    with pytest.raises(SituationParsingError, match="nur eine Person"):
        simulation.calculate("kibg_beitrag_total", MONAT)


def test_f4_partnerin_als_gesuchstellerin():
    simulation = p1(mutter=ohne("kibg_gesuchstellend"), partner=True)
    with pytest.raises(SituationParsingError, match="erziehungsberechtigte Person"):
        simulation.calculate("kibg_beitrag_total", MONAT)


def test_f5_getrennte_eltern_beide_erfasst():
    # Art. 2 Abs. 1 KiBG: Bei getrennten Eltern ist nur die gesuchstellende
    # Person erziehungsberechtigt; der andere Elternteil wird nicht erfasst.
    simulation = p1(gemeinsam=False)
    with pytest.raises(SituationParsingError, match="nur die gesuchstellende Person"):
        simulation.calculate("kibg_beitrag_total", MONAT)


def test_f6_gemeinsamer_haushalt_mit_einer_person():
    # Ein gemeinsamer Haushalt der Erziehungsberechtigten (Art. 8 Abs. 1
    # lit. a KiBV) setzt zwei Erziehungsberechtigte voraus.
    personen = {
        "mutter": {
            "wohnsitz_kanton_sg": {MONAT: True},
            "beschaeftigungsgrad": {MONAT: 1.0},
            "me_steuerveranlagung": {"2028": 60000},
        },
        "lina": {
            "geburtsdatum": {"ETERNITY": "2027-09-01"},
            "kibg_einrichtungstyp": {MONAT: "kita"},
            "kibg_einrichtung_anerkannt": {MONAT: True},
            "kibg_einrichtung_angemeldet": {MONAT: True},
            "betreuungsstunden": {MONAT: 80},
            "betreuungstage_mit_obhut": {MONAT: 8},
            "kibg_betreuungskosten": {MONAT: 1040},
        },
    }
    haushalt = {
        "erziehungsberechtigte": ["mutter"],
        "kinder": ["lina"],
        "gemeinsamer_haushalt": {MONAT: True},
    }
    simulation = SimulationBuilder().build_from_entities(
        SYSTEM, {"persons": personen, "households": {"familie": haushalt}}
    )
    with pytest.raises(SituationParsingError, match="zwei Erziehungsberechtigte"):
        simulation.calculate("kibg_beitrag_total", MONAT)


def test_f7_stunden_ohne_betreuungstage():
    simulation = p1(lina=lambda k: {**k, "betreuungstage_mit_obhut": {MONAT: 0}})
    with pytest.raises(SituationParsingError, match="keine Betreuungstage"):
        simulation.calculate("kibg_beitrag_total", MONAT)


def test_f8_kleinkind_als_eingeschult():
    simulation = p1(lina=lambda k: {**k, "eingeschult": {MONAT: True}})
    with pytest.raises(SituationParsingError, match="nicht eingeschult sein"):
        simulation.calculate("kibg_beitrag_total", MONAT)


def test_f9_negatives_aktuelles_einkommen():
    simulation = p1(mutter=lambda m: {**m, "me_aktuell": {"2028": -5000}})
    with pytest.raises(SituationParsingError, match="nicht negativ"):
        simulation.calculate("kibg_beitrag_total", MONAT)
