"""Beispielsituationen für die Web-API (OpenAPI-Spezifikation)."""

import json
import os

DIR_PATH = os.path.dirname(os.path.abspath(__file__))


def parse(file_name):
    """Load json example situations."""
    file_path = os.path.join(DIR_PATH, file_name)
    with open(file_path, encoding="utf8") as file:
        return json.loads(file.read())


# P1 aus challenge/szenarien.md: Paar, ein Kleinkind in der Kita
p1_paar_kita = parse("p1_paar_kita.json")
