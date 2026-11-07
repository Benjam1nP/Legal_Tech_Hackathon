# Rulebook: KiBG in OpenFisca

How we write the St. Gallen childcare support rules (KiBG) as OpenFisca code,
and what is checked automatically before every push.

## 0. One-time setup (every teammate)

```bash
bash tools/setup.sh
```

This installs OpenFisca and its tools, switches on the checks for every commit
and push, and sets up the commit message template. Requirements: `git`, `bash`
and [`uv`](https://docs.astral.sh/uv/getting-started/installation/).

Useful commands (run from the repository root):

| What | Command |
|---|---|
| Run all push checks now | `uv run --project openfisca-CH-SG pre-commit run --all-files --hook-stage pre-push` |
| Only the rulebook checker | `uv run --project openfisca-CH-SG python tools/check_openfisca.py` |
| Only the OpenFisca tests | `cd openfisca-CH-SG && make test` |
| Rebuild the documentation file locally | `uv run --project openfisca-CH-SG python tools/build_changelog.py` |

## 1. Where our code goes

The model lives in `openfisca-CH-SG/openfisca_ch_sg/`. Everything that came
with the OpenFisca template (basic income, housing tax, parenting allowance,
...) is **demo material that we replace** with the rules from the KiBG and its
ordinance:

| What | Folder |
|---|---|
| Fixed values from the text (rates, income limits, thresholds, ages, hour caps), each with its article | `parameters/` |
| Inputs and formulas (eligibility, determining income, support amount, caps) | `variables/` |
| Who the rules apply to (roles such as adult, child, partner) | `entities.py` |
| Hand-calculated cases per article, as proof that each rule matches the text | `tests/` |

**Format reference:** an untouched copy of the original template is kept in
[`docs/openfisca-template-reference/`](docs/openfisca-template-reference/).
OpenFisca does not load it. Look there for how variables, parameters, tests,
entities and reforms are written. Section 5 below shows the short version.

While demo files are still in the package, the checker shows warnings for them
(placeholder references and so on). These disappear once the demo is replaced.

## 2. The OpenFisca principles we follow

From the *Introduction to OpenFisca* (slide "An OpenFisca model is a set of rules"):

1. **Computable rules only: human decisions are inputs.** Whatever an authority
   decides with discretion (e.g. whether a care need is recognised, whether a
   case is a hardship) is an **input variable without a formula**. We never
   compute a discretionary decision.
2. **Strictly code the official text: line-to-line match.** One rule in the law =
   one variable or parameter, named after what the law says, with the exact
   article as `reference`. No "smart" shortcuts that merge several provisions.
3. **Users can plug in their own data.** Inputs have clear names, units and
   labels so a questionnaire or dataset can fill them.
4. **The 4 key concepts:**
   - **Periods**: every rule has a start date and every parameter value has a
     date. See "Start date" below.
   - **Parameters**: every amount, rate, threshold and age limit from the law
     goes into `parameters/*.yaml`, never into Python code.
   - **Entities**: say *who* the rule applies to, with the terms of the text:
     Erziehungsberechtigte and Kind (Art. 2 Abs. 1 KiBG), the gemeinsamer or
     getrennter Haushalt of the Erziehungsberechtigten (Art. 8 Abs. 1 lit. a/b
     KiBV), and the Partnerin or Partner in a gefestigte Lebensgemeinschaft who
     is not erziehungsberechtigt (Art. 8 Abs. 1 lit. b and Abs. 2 KiBV).
   - **Variables**: everything that is calculated or entered.

### Names: German legal terms

Variables and parameters are named with the **German terms of the text**, so the
lawyers in the team can compare code and text line by line:

- snake_case, ASCII only: `massgebendes_einkommen`, `erziehungsberechtigte`,
  `kostenobergrenze` (ä → ae, ö → oe, ü → ue; the checker warns on umlauts).
- `label` in German, close to the wording of the article.
- Prefix `kibg_` for variables and parameters specific to the childcare
  contribution (`kibg_anspruch`, `kibg.einkommen.min`); general facts without
  prefix (`geburtsdatum`, `beschaeftigungsgrad`). See
  `challenge/line-to-line-rules.md`.
- Shares as fractions with unit `/1`: 80 % is `0.8`, 120 % is `1.20`.

### Start date

The Vollzugsbeginn is still open: the government sets it (KiBG Ziff. IV Nr. 1)
and the KiBV applies "ab ●●" (KiBV Ziff. IV). Until it is known, we use the
**placeholder 1 August 2028**:

- formulas: `formula_2028_08`
- parameter values: `2028-08-01`
- tests: `period: 2028-08` or later

When the real date is published, replace these everywhere and record it as a
`Decision:`.

## 3. Legal sources and citation

| Source | File | Status |
|---|---|---|
| Gesetz über Beiträge für familien- und schulergänzende Kinderbetreuung (**KiBG**) | `challenge/Gesetz.pdf` | The PDF is the *result of the first reading* (16 Sept 2025). The law was adopted on 14 June 2026. **Check provisions against the adopted version.** |
| Verordnung über Beiträge für familien- und schulergänzende Kinderbetreuung (**KiBV**, footnote 2 of the draft) | `challenge/Verordnung.pdf` | **Draft** (RRB 2026/733), open for comments until 15 Nov 2026. Not in force. |

Citation format for `reference`:

- Law: `Art. 6 Abs. 2 KiBG`
- Ordinance: `Art. 8 Abs. 1 lit. b KiBV (Entwurf)`
- Add the official URL when available, e.g.
  `reference = ["Art. 6 Abs. 2 KiBG", "https://www.sg.ch/..."]`

Every KiBV reference must say `(Entwurf)`, so rules in force and draft rules can
always be told apart. The checker warns if it is missing.

## 4. What is checked, and when

| When | Check | Blocks? |
|---|---|---|
| every commit | ruff lint + auto-format (Python) | yes |
| every commit | yamllint (YAML syntax and style) | yes |
| every push | everything above + **all OpenFisca tests** | yes |
| every push | **rulebook checker** (`tools/check_openfisca.py`) | see below |
| on GitHub, every push | the same push checks again (`.github/workflows/checks.yaml`) | shows a red X |
| on demand | `docs/CHANGELOG_DECISIONS.md` is rebuilt (see section 6) | – |

### Rulebook checker: errors (block the push)

- Variable is missing `value_type`, `entity`, `definition_period` or `label`.
- Variable name is defined twice.
- Parameter is missing `description`.
- Parameter value is not keyed by a date (`YYYY-MM-DD`) or has no `value:`.
- Test case is missing `period` or `output`.
- Invalid Python or YAML.

### Rulebook checker: warnings (shown, never block)

- No `reference`, a placeholder reference (`example`), or a reference without
  an article (`Art. ...`).
- KiBV reference without `(Entwurf)`, or the ordinance cited as "Verordnung KiBG".
- Parameter without `metadata.unit` (`currency-CHF`, `/1` for rates, `year`, ...).
- Hard-coded numbers other than 0 and 1 in a formula (should be a parameter).
- Variable with a formula but no test case in `tests/`.
- Variable name not in snake_case or with umlauts; test case without `name`.

## 5. Examples of the expected format

Variable (`variables/beitrag.py`), coding Art. 6 Abs. 2 KiBG ("Ein Beitrag darf
die Kosten der Erziehungsberechtigten für das in Anspruch genommene
Betreuungsangebot nicht übersteigen"):

```python
from openfisca_core.model_api import min_
from openfisca_core.periods import MONTH
from openfisca_core.variables import Variable

from openfisca_ch_sg.entities import Household


class beitrag(Variable):
    value_type = float
    entity = Household
    definition_period = MONTH
    label = "Beitrag, begrenzt auf die Kosten des Betreuungsangebots"
    reference = "Art. 6 Abs. 2 KiBG"

    def formula_2028_08(haushalt, period, parameters):
        beitrag_linear = haushalt("beitrag_lineares_modell", period)  # Art. 6 Abs. 1
        kosten = haushalt("kosten_betreuungsangebot", period)
        return min_(beitrag_linear, kosten)
```

Parameter (`parameters/einkommensgrenze.yaml`). Article and number are
placeholders; take both from the text:

```yaml
description: Obergrenze des massgebenden Einkommens
metadata:
  unit: currency-CHF
  reference: Art. X Abs. Y KiBV (Entwurf)
values:
  2028-08-01:
    value: 100000
```

Test (`tests/beitrag.yaml`), calculated by hand from the article:

```yaml
- name: Beitrag übersteigt die Kosten nicht (Art. 6 Abs. 2 KiBG)
  period: 2028-08
  input:
    beitrag_lineares_modell: 900
    kosten_betreuungsangebot: 700
  output:
    beitrag: 700
```

## 6. Commit messages and the documentation file

Every interpretation of the law, assumption, open question and use of AI goes
into the **commit message**, using the template that opens with `git commit`:

```text
Add Einkommen der Partnerin/des Partners (Art. 8 Abs. 1 lit. b KiBV)

Decision: Income of a partner counts only if they share the household in a gefestigte Lebensgemeinschaft and are not erziehungsberechtigt
Area: legal
Reason: Wording of Art. 8 Abs. 1 lit. b KiBV; "gefestigt" is defined in Abs. 2
Source: Art. 8 Abs. 1 lit. b und Abs. 2 KiBV (Entwurf)
Question: Is the two-year Konkubinat (Art. 8 Abs. 2 lit. b KiBV) measured at the application date or for each month?
AI: Claude Code: drafted the formula and test, checked by the team against the text
```

| Line | Use for | Goes to |
|---|---|---|
| `Decision:` + `Area:`, `Reason:`, `Source:` | interpretations, assumptions, design choices | decision table of the section given by `Area:` |
| `Area:` | `function`, `design`, `legal`, `ethics`, `repro` or `team` | one of the 6 report sections |
| `Status: superseded ...` | restate an old `Decision:` text to retire it | shown struck through |
| `Question:` | open legal questions, ambiguities in the text | section 3 |
| `AI:` | every use of an AI tool | section 6, Statement of AI Use |
| `External:` | libraries, templates, sources used | section 6 |

**`docs/CHANGELOG_DECISIONS.md`** is generated from these lines and from the
code. Its sections follow the evaluation criteria of the course syllabus:
functionality, technical design, legal–technical integration (with a table of
which article is encoded where), responsible design, reproducibility, and team
contribution with AI use. That makes it the starting point for the report.

It is **not** rebuilt on every push (that would add a bot commit each time).
Rebuild it on demand, **at least once before the submission on 8 Nov**:

- on GitHub: Actions → "Update changes and decisions" → Run workflow, then `git pull`
- or locally: `uv run --project openfisca-CH-SG python tools/build_changelog.py`,
  then commit the file

Don't edit the file by hand; it is regenerated each time.

## 7. Working together

`tools/setup.sh` sets `pull.rebase true`, so `git pull` never creates merge
commits. If a push is rejected because a teammate pushed first: `git pull`,
then push again.

`git push --no-verify` skips the local checks. Only use it if a check is broken
rather than your code. GitHub still runs the checks and shows a red X. Fix it
right away.
