#!/usr/bin/env python3
"""Rulebook checker for the KiBG OpenFisca model.

Runs before every push (and in CI). See RULEBOOK.md for the rules.

ERRORS block the push:   broken OpenFisca format.
WARNINGS never block:    legal references, hard-coded numbers, missing tests.

Usage:
    python tools/check_openfisca.py
"""

from __future__ import annotations

import ast
import datetime as dt
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
PKG = ROOT / "openfisca-CH-SG" / "openfisca_ch_sg"
VARIABLES = PKG / "variables"
PARAMETERS = PKG / "parameters"
TESTS = PKG / "tests"

REQUIRED_VARIABLE_ATTRS = ("value_type", "entity", "definition_period", "label")
ARTICLE_RE = re.compile(r"\b(art\.?|artikel|article)\s*\d", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"example", re.IGNORECASE)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ALLOWED_NUMBERS = {0, 1}
PARAM_META_KEYS = {"description", "metadata", "documentation", "reference"}

errors: list[str] = []
warnings: list[str] = []


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def error(path: Path, line: int | None, msg: str) -> None:
    errors.append(f"{rel(path)}{f':{line}' if line else ''}: {msg}")


def warn(path: Path, line: int | None, msg: str) -> None:
    warnings.append(f"{rel(path)}{f':{line}' if line else ''}: {msg}")


def check_reference(path: Path, line: int | None, texts: list[str], what: str) -> None:
    joined = " ".join(texts).strip()
    if not joined:
        warn(path, line, f"{what} has no legal reference")
        return
    if PLACEHOLDER_RE.search(joined):
        warn(path, line, f"{what} still uses a placeholder reference ({joined!r})")
    if not ARTICLE_RE.search(joined):
        warn(path, line, f"{what} reference does not name an article (Art. ...)")


# --------------------------------------------------------------------------
# Variables
# --------------------------------------------------------------------------


def variable_classes(tree: ast.AST):
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef) and any(
            (isinstance(b, ast.Name) and b.id == "Variable")
            or (isinstance(b, ast.Attribute) and b.attr == "Variable")
            for b in node.bases
        ):
            yield node


def string_constants(node: ast.AST) -> list[str]:
    return [
        n.value
        for n in ast.walk(node)
        if isinstance(n, ast.Constant) and isinstance(n.value, str)
    ]


def check_variables() -> dict[str, tuple]:
    """Return {variable_name: (path, line, has_formula)}."""
    found: dict[str, tuple] = {}
    for path in sorted(VARIABLES.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError as exc:
            error(path, exc.lineno, f"syntax error: {exc.msg}")
            continue

        for cls in variable_classes(tree):
            name = cls.name
            if name in found:
                error(path, cls.lineno, f"variable '{name}' is defined twice")
            if name != name.lower():
                warn(path, cls.lineno, f"variable '{name}' should be snake_case")

            attrs = {
                target.id: stmt
                for stmt in cls.body
                if isinstance(stmt, ast.Assign)
                for target in stmt.targets
                if isinstance(target, ast.Name)
            }
            for attr in REQUIRED_VARIABLE_ATTRS:
                if attr not in attrs:
                    error(path, cls.lineno, f"variable '{name}' is missing '{attr}'")
            if (
                "label" in attrs
                and not "".join(string_constants(attrs["label"].value)).strip()
            ):
                error(path, cls.lineno, f"variable '{name}' has an empty label")

            ref = attrs.get("reference")
            check_reference(
                path,
                cls.lineno,
                string_constants(ref.value) if ref else [],
                f"variable '{name}'",
            )

            formulas = [
                f
                for f in cls.body
                if isinstance(f, ast.FunctionDef) and f.name.startswith("formula")
            ]
            for formula in formulas:
                check_hard_coded_numbers(path, name, formula)
            found[name] = (path, cls.lineno, bool(formulas))
    return found


def check_hard_coded_numbers(path: Path, var_name: str, formula) -> None:
    for node in ast.walk(formula):
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, (int, float))
            and not isinstance(node.value, bool)
            and node.value not in ALLOWED_NUMBERS
        ):
            warn(
                path,
                node.lineno,
                f"'{var_name}' hard-codes the number {node.value}; "
                "legal amounts/rates/thresholds belong in parameters/",
            )


# --------------------------------------------------------------------------
# Parameters
# --------------------------------------------------------------------------


def find_reference(doc) -> list[str]:
    refs = []
    if isinstance(doc, dict):
        for key, value in doc.items():
            if key == "reference":
                if isinstance(value, list):
                    refs.extend(
                        str(
                            v.get("title", v.get("href", v))
                            if isinstance(v, dict)
                            else v
                        )
                        for v in value
                    )
                elif isinstance(value, dict):
                    refs.extend(str(v) for v in value.values())
                else:
                    refs.append(str(value))
            elif key != "values":
                refs.extend(find_reference(value))
    return refs


def check_parameter(path: Path, name: str, doc: dict) -> None:
    what = f"parameter '{name}'"
    if not str(doc.get("description", "")).strip():
        error(path, None, f"{what} is missing a 'description'")
    metadata = doc.get("metadata") or {}
    if "values" in doc and "unit" not in metadata:
        warn(path, None, f"{what} has no metadata.unit (e.g. currency-CHF, /1, year)")
    check_reference(path, None, find_reference(doc), what)

    if "values" in doc:
        values = doc["values"]
        if not isinstance(values, dict) or not values:
            error(path, None, f"{what}: 'values' must be a non-empty mapping of dates")
            return
        for key, entry in values.items():
            if not (
                isinstance(key, dt.date)
                or (isinstance(key, str) and DATE_RE.match(key))
            ):
                error(path, None, f"{what}: '{key}' is not a date (use YYYY-MM-DD)")
            # Allowed: "expected", short form "2026-01-01: 10", or "value: ..."
            if entry == "expected" or isinstance(entry, (int, float)):
                continue
            if not isinstance(entry, dict) or "value" not in entry:
                error(
                    path,
                    None,
                    f"{what}: entry for {key} needs 'value:' (or 'expected')",
                )
    elif not isinstance(doc["brackets"], list) or not doc["brackets"]:
        error(path, None, f"{what}: 'brackets' must be a non-empty list")


def walk_parameter_doc(path: Path, name: str, doc) -> None:
    if not isinstance(doc, dict):
        error(path, None, f"'{name}' must be a mapping")
        return
    if "values" in doc or "brackets" in doc:
        check_parameter(path, name, doc)
        return
    for key, child in doc.items():
        if key in PARAM_META_KEYS:
            continue
        walk_parameter_doc(path, f"{name}.{key}", child)


def check_parameters() -> None:
    for path in sorted(PARAMETERS.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix != ".yaml":
            error(path, None, "parameter files must use the .yaml extension")
            continue
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            error(path, None, f"invalid YAML: {exc}")
            continue
        if path.name == "index.yaml":
            if not isinstance(doc, dict) or not str(doc.get("description", "")).strip():
                warn(path, None, "index.yaml should have a 'description'")
            continue
        walk_parameter_doc(path, path.stem, doc)


# --------------------------------------------------------------------------
# Tests
# --------------------------------------------------------------------------


def collect_output_names(output: dict) -> set[str]:
    """Output can be flat {var: value} or by entity {persons: {id: {var: value}}}."""
    names = set()
    for key, value in output.items():
        names.add(key)
        if isinstance(value, dict):
            names |= collect_output_names(value)
    return names


def check_tests(variables: dict[str, tuple]) -> None:
    tested: set[str] = set()
    for path in sorted(TESTS.rglob("*")):
        if not path.is_file() or path.suffix not in {".yaml", ".yml"}:
            continue
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            error(path, None, f"invalid YAML: {exc}")
            continue
        cases = doc if isinstance(doc, list) else [doc]
        for i, case in enumerate(cases, 1):
            if not isinstance(case, dict):
                error(path, None, f"test #{i} must be a mapping")
                continue
            label = case.get("name") or f"test #{i}"
            if "name" not in case:
                warn(path, None, f"{label} has no 'name'")
            for key in ("period", "output"):
                if key not in case:
                    error(path, None, f"{label} is missing '{key}'")
            output = case.get("output") or {}
            if isinstance(output, dict):
                tested |= collect_output_names(output)

    for name, (path, line, has_formula) in variables.items():
        if has_formula and name not in tested:
            warn(path, line, f"variable '{name}' has no test in {rel(TESTS)}/")


# --------------------------------------------------------------------------


def main() -> int:
    variables = check_variables()
    check_parameters()
    check_tests(variables)

    print(f"Rulebook check: {len(variables)} variable(s) inspected.")
    if warnings:
        print(f"\n{len(warnings)} warning(s) (not blocking):")
        for w in warnings:
            print(f"  WARN  {w}")
    if errors:
        print(f"\n{len(errors)} error(s) (push blocked, see RULEBOOK.md):")
        for e in errors:
            print(f"  ERROR {e}")
        return 1
    print("\nNo blocking errors.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
