"""Eingabefehler F1 bis F4 aus challenge/szenarien.md (Teil 3b).

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


def p1(mutter=None, vater=None, lina=None, partner=False):
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
        "gemeinsamer_haushalt": {MONAT: True},
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
