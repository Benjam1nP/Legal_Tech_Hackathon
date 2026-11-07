"""Der Vollzugsbeginn steht an drei Stellen und muss überall gleich sein.

1. VOLLZUGSBEGINN in hilfsfunktionen.py (für die Datumsregeln)
2. Name der Formeln: formula_2028_08
3. Erstes Datum jedes Parameters: 2028-08-01

Legt der Kanton den Vollzugsbeginn fest, alle drei ändern (README, Abschnitt
«Vollzugsbeginn ändern»). Dieser Test zeigt, wenn eine Stelle vergessen wurde.
"""

from openfisca_ch_sg import CountryTaxBenefitSystem
from openfisca_ch_sg.hilfsfunktionen import VOLLZUGSBEGINN

SYSTEM = CountryTaxBenefitSystem()
BEGINN = VOLLZUGSBEGINN.isoformat()
OHNE_DATUM = "0001-01-01"  # Formeln mit dem Namen «formula» gelten immer


def test_formeln_beginnen_am_vollzugsbeginn():
    abweichend = {
        name: start
        for name, variable in SYSTEM.variables.items()
        for start in variable.formulas
        if start not in (BEGINN, OHNE_DATUM)
    }
    assert abweichend == {}, f"Formeln mit anderem Startdatum: {abweichend}"


def test_parameter_beginnen_am_vollzugsbeginn():
    abweichend = {}
    for parameter in SYSTEM.parameters.kibg.get_descendants():
        werte = getattr(parameter, "values_list", None)
        if werte:
            erstes = min(wert.instant_str for wert in werte)
            if erstes != BEGINN:
                abweichend[parameter.name] = erstes
    assert abweichend == {}, f"Parameter mit anderem ersten Datum: {abweichend}"
