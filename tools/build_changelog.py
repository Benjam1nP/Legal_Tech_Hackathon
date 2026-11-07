#!/usr/bin/env python3
"""Build docs/CHANGELOG_DECISIONS.md: the raw material for the project report.

The file is structured along the evaluation criteria for the "legal and
technical documentation" in the course syllabus, so each section can be
turned into a report chapter:

    1. Functionality and prototype quality
    2. Technical design and architecture
    3. Legal and technical integration
    4. Responsible and ethical technology design
    5. Documentation and reproducibility
    6. Team contribution and transparency (incl. AI use statement)
    Appendix: chronological change log

Content comes from two places:
- the code itself (which articles are encoded where, number of tests, ...)
- commit messages, using these lines (see RULEBOOK.md and .gitmessage):

    Decision: <what we decided>      starts a new decision
    Area:     legal | function | design | ethics | repro | team
    Reason:   <why>
    Source:   <Art. X Abs. Y KiBG / KiBV (Entwurf) / team decision>
    Status:   superseded (optional; restate the same Decision text)
    Question: <open legal question or ambiguity>
    AI:       <tool>: <what it was used for>
    External: <resource>: <what it was used for>

Restating an existing Decision text in a later commit updates its fields
(e.g. to add an Area or mark it superseded).

The file is fully regenerated on every run. It is updated on demand: on
GitHub (Actions -> "Update changes and decisions" -> Run workflow) or locally:

    uv run --project openfisca-CH-SG python tools/build_changelog.py
    uv run --project openfisca-CH-SG python tools/build_changelog.py --check
"""

from __future__ import annotations

import argparse
import ast
import re
import subprocess
import sys
from pathlib import Path

import tomllib
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_openfisca as chk

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "docs" / "CHANGELOG_DECISIONS.md"
BOT_MARK = "[changelog-bot]"
MAX_FILES = 12
REC, UNIT = "\x1e", "\x1f"

FIELDS = ("decision", "area", "reason", "source", "status")
SINGLE_FIELDS = ("question", "ai", "external")
FIELD_RE = re.compile(
    r"^\s*(Decision|Area|Reason|Source|Status|Question|AI|External)\s*:\s*(.*)$",
    re.IGNORECASE,
)

AREAS = {
    "function": "1. Functionality and prototype quality",
    "design": "2. Technical design and architecture",
    "legal": "3. Legal and technical integration",
    "ethics": "4. Responsible and ethical technology design",
    "repro": "5. Documentation and reproducibility",
    "team": "6. Team contribution and transparency",
}

INTROS = {
    "function": "_Syllabus: the prototype demonstrates the core idea and shows that "
    "the solution can work in practice._",
    "design": "_Syllabus: the technical structure is understandable, fits the goal "
    "and rests on deliberate design choices._",
    "legal": "_Syllabus: the technical solution clearly responds to the legal "
    "problem identified by the team._",
    "ethics": "_Syllabus: awareness of privacy, security, fairness, transparency, "
    "accountability and the limits of automation._",
    "repro": "_Syllabus: clear instructions on how the prototype works, how it can "
    "be tested and which dependencies or tools are used._",
    "team": "_Syllabus: each member's contribution, and disclosure of AI tools, "
    "open-source components and external resources (Statement of Author "
    "Contribution and AI Use)._",
}

ARTICLE_RE = re.compile(
    r"Art\.?\s*(\d+)([a-z]{0,3})\b(?:\s*Abs\.?\s*(\d+))?", re.IGNORECASE
)


# --------------------------------------------------------------------------
# Git history
# --------------------------------------------------------------------------


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout


def load_commits() -> list[dict]:
    """Oldest first."""
    fmt = UNIT.join(["%H", "%h", "%aN", "%ad", "%s", "%b"]) + REC
    raw = git(
        "log",
        "--reverse",
        "--no-merges",
        "--date=format:%Y-%m-%d %H:%M",
        f"--format={fmt}",
    )
    commits = []
    for record in raw.split(REC):
        record = record.strip("\n")
        if not record:
            continue
        full, short, author, date, subject, body = record.split(UNIT)
        if BOT_MARK in subject:
            continue
        files = [
            line
            for line in git("show", "--name-status", "--format=", full).splitlines()
            if line.strip()
        ]
        commit = {
            "short": short,
            "author": author,
            "date": date,
            "subject": subject,
            "files": files,
        }
        commit.update(parse_body(body))
        commits.append(commit)
    return commits


def parse_body(body: str) -> dict:
    decisions: list[dict] = []
    singles: dict[str, list[str]] = {key: [] for key in SINGLE_FIELDS}
    for line in body.splitlines():
        match = FIELD_RE.match(line)
        if not match:
            continue
        key, value = match.group(1).lower(), match.group(2).strip()
        if not value:
            continue
        if key in SINGLE_FIELDS:
            singles[key].append(value)
        elif key == "decision":
            decisions.append({"decision": value})
        elif decisions:
            decisions[-1][key] = value
    return {"decisions": decisions, **singles}


def merge_decisions(commits: list[dict]) -> list[dict]:
    """One entry per decision text; later restatements update the fields."""
    merged: dict[str, dict] = {}
    for c in commits:
        for d in c["decisions"]:
            key = " ".join(d["decision"].lower().split())
            entry = merged.setdefault(
                key, {"date": c["date"][:10], "commits": [], "authors": []}
            )
            entry.update({k: v for k, v in d.items() if k in FIELDS})
            entry["commits"].append(c["short"])
            if c["author"] not in entry["authors"]:
                entry["authors"].append(c["author"])
    return list(merged.values())


# --------------------------------------------------------------------------
# The model itself
# --------------------------------------------------------------------------


def model_elements() -> list[dict]:
    """Variables and parameters with their legal references."""
    elements = []
    for path in sorted(chk.VARIABLES.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for cls in chk.variable_classes(tree):
            ref = ""
            has_formula = False
            for stmt in cls.body:
                if isinstance(stmt, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "reference"
                    for t in stmt.targets
                ):
                    ref = "; ".join(chk.string_constants(stmt.value))
                if isinstance(stmt, ast.FunctionDef) and stmt.name.startswith(
                    "formula"
                ):
                    has_formula = True
            elements.append(
                {
                    "name": cls.name,
                    "kind": "formula" if has_formula else "input",
                    "reference": ref,
                    "path": path,
                }
            )

    def walk(path, name, doc):
        if not isinstance(doc, dict):
            return
        if "values" in doc or "brackets" in doc:
            elements.append(
                {
                    "name": name,
                    "kind": "parameter",
                    "reference": "; ".join(chk.find_reference(doc)),
                    "path": path,
                }
            )
            return
        for key, child in doc.items():
            if key not in chk.PARAM_META_KEYS:
                walk(path, f"{name}.{key}", child)

    for path in sorted(chk.PARAMETERS.rglob("*.yaml")):
        if path.name == "index.yaml":
            continue
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        prefix = ".".join(path.relative_to(chk.PARAMETERS).with_suffix("").parts)
        walk(path, prefix, doc)
    return elements


def count_tests() -> tuple[int, int]:
    files = cases = 0
    for path in chk.TESTS.rglob("*.y*ml"):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError:
            continue
        files += 1
        cases += len(doc) if isinstance(doc, list) else 1
    return files, cases


def act_of(reference: str) -> str:
    if "KiBV" in reference:
        return "KiBV"
    if "KiBG" in reference:
        return "KiBG"
    return "other"


def article_sort_key(element: dict):
    match = ARTICLE_RE.search(element["reference"])
    order = {"KiBG": 0, "KiBV": 1, "other": 2}[act_of(element["reference"])]
    if not match:
        return (order, 9999, "", 0, element["name"])
    return (
        order,
        int(match.group(1)),
        match.group(2) or "",
        int(match.group(3) or 0),
        element["name"],
    )


def locked_versions(*packages: str) -> dict[str, str]:
    lock = ROOT / "openfisca-CH-SG" / "uv.lock"
    try:
        data = tomllib.loads(lock.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return {}
    return {
        p["name"]: p["version"]
        for p in data.get("package", [])
        if p.get("name") in packages and "version" in p
    }


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------


def cell(text: str) -> str:
    return str(text).replace("|", "\\|").replace("\n", " ")


def table(header: list[str], rows: list[list[str]]) -> list[str]:
    out = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    out += ["| " + " | ".join(cell(c) for c in row) + " |" for row in rows]
    return out


def decision_table(decisions: list[dict]) -> list[str]:
    if not decisions:
        return ["_No decisions recorded yet._"]
    rows = []
    for d in decisions:
        text = d["decision"]
        status = d.get("status", "").strip()
        if status.lower().startswith("superseded"):
            text = f"~~{text}~~ ({status})"
        rows.append(
            [
                d["date"],
                text,
                d.get("reason", "–"),
                d.get("source", "–"),
                ", ".join(f"`{s}`" for s in d["commits"]),
                ", ".join(d["authors"]),
            ]
        )
    return table(["Date", "Decision", "Reason", "Source", "Commit", "By"], rows)


def bullet_list(items: list[tuple[dict, str]]) -> list[str]:
    return [
        f"- {text} (`{c['short']}`, {c['author']}, {c['date'][:10]})"
        for c, text in items
    ]


def path_area(path: str) -> str:
    if path.startswith(("docs/", "RULEBOOK")):
        return "docs"
    if "/variables/" in path or "/parameters/" in path or path.endswith("entities.py"):
        return "rules"
    if "/tests/" in path:
        return "tests"
    if path.startswith(("tools/", ".github/", ".pre-commit")):
        return "tooling"
    if path.endswith(".md"):
        return "docs"
    if path.startswith("challenge/"):
        return "materials"
    return "other"


def render_function(elements: list[dict]) -> list[str]:
    files, cases = count_tests()
    kinds = {
        k: sum(e["kind"] == k for e in elements)
        for k in ("input", "formula", "parameter")
    }
    return [
        "**Current state of the model** (generated from the code):",
        "",
        f"- Variables with a formula: {kinds['formula']}",
        (
            "- Input variables (facts and human decisions entered by the user): "
            f"{kinds['input']}"
        ),
        f"- Parameters (values taken from the legal text): {kinds['parameter']}",
        f"- Test cases: {cases} in {files} file(s)",
        "",
    ]


def render_legal(elements: list[dict]) -> list[str]:
    with_article = [e for e in elements if ARTICLE_RE.search(e["reference"])]
    without = len(elements) - len(with_article)
    out = [
        "**Legal sources**",
        "",
        *table(
            ["Act", "Document", "Status"],
            [
                [
                    (
                        "Gesetz über Beiträge für familien- und schulergänzende "
                        "Kinderbetreuung (KiBG)"
                    ),
                    (
                        "`challenge/Gesetz.pdf` (result of the first reading, "
                        "16 Sept 2025)"
                    ),
                    (
                        "Adopted 14 June 2026; Vollzugsbeginn set by the government "
                        "(KiBG Ziff. IV Nr. 1), still open"
                    ),
                ],
                [
                    (
                        "Verordnung über Beiträge für familien- und schulergänzende "
                        "Kinderbetreuung (KiBV)"
                    ),
                    "`challenge/Verordnung.pdf` (RRB 2026/733)",
                    (
                        "Draft, consultation until 15 Nov 2026; applies from ●● "
                        "(KiBV Ziff. IV)"
                    ),
                ],
            ],
        ),
        "",
        (
            "**Encoded provisions** (generated from the `reference` of every variable "
            "and parameter):"
        ),
        "",
    ]
    if with_article:
        rows = []
        for e in sorted(with_article, key=article_sort_key):
            ref = e["reference"]
            draft = "draft" if ("KiBV" in ref or "Entwurf" in ref) else "law"
            rows.append(
                [ref, f"`{e['name']}`", e["kind"], draft, f"`{chk.rel(e['path'])}`"]
            )
        out += table(["Reference", "Element", "Kind", "Source status", "File"], rows)
    else:
        out.append("_No element references an article yet._")
    if without:
        out += [
            "",
            (
                f"_{without} element(s) in the model have no article reference "
                "(template demo or still to be documented; see the checker warnings)._"
            ),
        ]
    return out + [""]


def render_repro() -> list[str]:
    versions = locked_versions("openfisca-core", "ruff", "yamllint", "pre-commit")
    rows = [[name, version] for name, version in sorted(versions.items())]
    return [
        "**How to run and test** (details in `RULEBOOK.md`):",
        "",
        "```bash",
        "bash tools/setup.sh                       # install OpenFisca + checks",
        "cd openfisca-CH-SG && make test           # run all test cases",
        "cd openfisca-CH-SG && make serve-local    # OpenFisca Web API on :5000",
        "```",
        "",
        "**Pinned versions** (from `openfisca-CH-SG/uv.lock`):",
        "",
        *(table(["Package", "Version"], rows) if rows else ["_uv.lock not found._"]),
        "",
    ]


def render_team(commits: list[dict]) -> list[str]:
    people: dict[str, dict] = {}
    for c in commits:
        key = c["author"].lower()
        p = people.setdefault(
            key, {"name": c["author"], "commits": 0, "first": c["date"], "areas": {}}
        )
        p["commits"] += 1
        p["last"] = c["date"]
        for line in c["files"]:
            area = path_area(line.split("\t")[-1])
            p["areas"][area] = p["areas"].get(area, 0) + 1
    rows = []
    for p in sorted(people.values(), key=lambda p: -p["commits"]):
        areas = ", ".join(
            f"{a} ({n})" for a, n in sorted(p["areas"].items(), key=lambda x: -x[1])
        )
        rows.append(
            [p["name"], str(p["commits"]), p["first"][:10], p["last"][:10], areas]
        )

    ai = [(c, t) for c in commits for t in c["ai"]]
    external = [(c, t) for c in commits for t in c["external"]]
    return [
        (
            "**Contributions from the git history** (file changes per area; imports "
            "of template code count as many files):"
        ),
        "",
        *table(["Member", "Commits", "First", "Last", "Files changed per area"], rows),
        "",
        (
            "_Add contributions that don't show in git (legal analysis, testing by "
            "hand, pitch, ...) by hand in the report._"
        ),
        "",
        (
            "**AI use** (from `AI:` lines; basis for the Statement of Author "
            "Contribution and AI Use):"
        ),
        "",
        *(bullet_list(ai) or ["_None recorded yet._"]),
        "",
        "**Open-source components and external resources** (from `External:` lines):",
        "",
        *(bullet_list(external) or ["_None recorded yet._"]),
        "",
    ]


def render_changelog(commits: list[dict]) -> list[str]:
    labels = {"A": "added", "M": "changed", "D": "deleted", "R": "renamed"}
    out = ["## Appendix: Change log", ""]
    current_day = None
    for c in reversed(commits):
        day = c["date"][:10]
        if day != current_day:
            if current_day is not None:
                out.append("")
            out += [f"### {day}", ""]
            current_day = day
        out.append(
            f"- **{c['subject']}** (`{c['short']}`, {c['author']}, {c['date'][11:]})"
        )
        for d in c["decisions"]:
            out.append(f"  - Decision: {d['decision']}")
        if c["files"]:
            items = []
            for line in c["files"][:MAX_FILES]:
                parts = line.split("\t")
                items.append(f"`{parts[-1]}` ({labels.get(parts[0][:1], parts[0])})")
            if len(c["files"]) > MAX_FILES:
                items.append(f"and {len(c['files']) - MAX_FILES} more")
            out.append(f"  - Files: {', '.join(items)}")
    return out


def render(commits: list[dict]) -> str:
    elements = model_elements()
    decisions = merge_decisions(commits)
    by_area: dict[str, list[dict]] = {area: [] for area in AREAS}
    unsorted = []
    for d in decisions:
        area = d.get("area", "").strip().lower()
        by_area.get(area, unsorted).append(d)

    questions = [(c, t) for c in commits for t in c["question"]]
    last = commits[-1] if commits else None
    out = [
        "# Project documentation: changes and decisions",
        "",
        "<!-- Generated by tools/build_changelog.py. Do not edit by hand: write",
        "     decisions into commit messages instead (see RULEBOOK.md). -->",
        "",
        (
            "Raw material for the legal and technical documentation. Sections follow "
            "the evaluation criteria in the course syllabus."
        ),
    ]
    if last:
        out += ["", f"_State as of commit `{last['short']}` ({last['date']})._"]
    out.append("")

    extra = {
        "function": render_function(elements),
        "legal": render_legal(elements),
        "repro": render_repro(),
    }
    for area, title in AREAS.items():
        out += [f"## {title}", "", INTROS[area], ""]
        out += extra.get(area, [])
        if area == "legal":
            out += [
                "**Open legal questions and ambiguities** (from `Question:` lines):",
                "",
                *(bullet_list(questions) or ["_None recorded yet._"]),
                "",
            ]
        if area == "team":
            out += render_team(commits)
        out += ["**Decisions**", "", *decision_table(by_area[area]), ""]

    if unsorted:
        out += [
            "## Decisions without area",
            "",
            "_Restate them in a commit with an `Area:` line to sort them._",
            "",
            *decision_table(unsorted),
            "",
        ]
    out += render_changelog(commits)
    return "\n".join(out).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="only report if outdated")
    args = parser.parse_args()

    content = render(load_commits())
    rel = OUTPUT.relative_to(ROOT)
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != content:
            print(f"{rel} is outdated")
            return 1
        print(f"{rel} is up to date")
        return 0

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(content, encoding="utf-8")
    print(f"Wrote {rel} ({len(content.splitlines())} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
