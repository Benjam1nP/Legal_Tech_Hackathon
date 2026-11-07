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
| Rebuild the change log locally | `python3 tools/build_changelog.py` |

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
   - **Periods**: every rule has a start date (`formula_2027_01`) and every
     parameter value has a date. Use the date the provision **enters into force**.
   - **Parameters**: every amount, rate, threshold and age limit from the law
     goes into `parameters/*.yaml`, never into Python code.
   - **Entities**: say *who* the rule applies to (person or household), as the
     law does (Erziehungsberechtigte, Kind, Familie).
   - **Variables**: everything that is calculated or entered.

## 3. Legal sources and citation

| Source | File | Status |
|---|---|---|
| Gesetz über Beiträge für familien- und schulergänzende Kinderbetreuung (**KiBG**) | `challenge/Gesetz.pdf` | The PDF is the *result of the first reading* (16 Sept 2025). The law was adopted on 14 June 2026. **Check provisions against the adopted version.** |
| Verordnung über Beiträge für familien- und schulergänzende Kinderbetreuung | `challenge/Verordnung.pdf` | **Draft** (RRB 2026/733), open for comments until 15 Nov 2026. Not in force. |

Citation format for `reference`:

- Law: `Art. 6 Abs. 1 KiBG`
- Ordinance: `Art. 3 Abs. 2 Verordnung KiBG (Entwurf)`
- Add the official URL when available, e.g.
  `reference = ["Art. 6 Abs. 1 KiBG", "https://www.sg.ch/..."]`

Rules taken from the draft ordinance must say `(Entwurf)` in the reference, so
rules in force and draft rules can always be told apart.

## 4. What is checked, and when

| When | Check | Blocks? |
|---|---|---|
| every commit | ruff lint + auto-format (Python) | yes |
| every commit | yamllint (YAML syntax and style) | yes |
| every push | everything above + **all OpenFisca tests** | yes |
| every push | **rulebook checker** (`tools/check_openfisca.py`) | see below |
| on GitHub, every push | the same push checks again (`.github/workflows/checks.yaml`) | shows a red X |
| on GitHub, push to `main` | `docs/CHANGELOG_DECISIONS.md` is rebuilt | – |

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
- Parameter without `metadata.unit` (`currency-CHF`, `/1` for rates, `year`, ...).
- Hard-coded numbers other than 0 and 1 in a formula (should be a parameter).
- Variable with a formula but no test case in `tests/`.
- Variable name not in snake_case; test case without `name`.

## 5. Examples of the expected format

Variable (`variables/eligibility.py`):

```python
from openfisca_core.periods import MONTH
from openfisca_core.variables import Variable

from openfisca_ch_sg.entities import Household


class kibg_income_limit_met(Variable):
    value_type = bool
    entity = Household
    definition_period = MONTH
    label = "Household income is below the KiBG income limit"
    reference = "Art. X Abs. Y KiBG"  # replace with the real article

    def formula_2027_01(household, period, parameters):
        limit = parameters(period).kibg.income_limit
        return household("kibg_determining_income", period) <= limit
```

Parameter (`parameters/income_limit.yaml`):

```yaml
description: Income limit for childcare contributions
metadata:
  unit: currency-CHF
  reference: Art. X Abs. Y Verordnung KiBG (Entwurf)
values:
  2027-01-01:
    value: 100000  # placeholder, take the number from the text
```

Test (`tests/eligibility.yaml`):

```yaml
- name: Household just below the income limit is eligible (Art. X KiBG)
  period: 2027-01
  input:
    kibg_determining_income: 99999
  output:
    kibg_income_limit_met: true
```

Numbers and dates above are placeholders, not legal values.

## 6. Commit messages, decisions and the change log

Every interpretation of the law, assumption or open question goes into the
**commit message**, using the template that opens with `git commit`:

```text
Add income limit for childcare contribution (Art. 6 KiBG)

Decision: Income limit is applied per household, not per parent
Reason: Art. 6 speaks of the "Familie"; confirmed in team call
Source: Art. 6 Abs. 1 KiBG
```

After every push to `main`, GitHub rebuilds **`docs/CHANGELOG_DECISIONS.md`**
from the git history: a table of all decisions and a dated list of all changes.
Don't edit that file by hand; it is regenerated each time. **Run `git pull`
after your push** to get the updated file.

## 7. Emergencies

`git push --no-verify` skips the local checks. Only use it if a check is broken
rather than your code. GitHub still runs the checks and shows a red X. Fix it
right away.
