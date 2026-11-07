# OpenFisca model for Sankt Gallen Canton (Switzerland)

Rules as Code for the contributions to family- and school-based childcare in
the Canton of St. Gallen: the law (KiBG, adopted 14 June 2026) and its
implementing ordinance (KiBV, draft RRB 2026/733). All values apply from the
placeholder start date **2028-08-01**, because the Vollzugsbeginn is not set
yet.

All modelling happens in the `openfisca_ch_sg` folder:

| Folder / file | Content |
|---|---|
| `entities.py` | Person and household of the applicant with the roles `erziehungsberechtigte`, `kinder` and `partner` |
| `parameters/kibg/` | Fixed values of the text, each with its article (rates, income limits, thresholds) |
| `variables/` | Inputs and formulas, one file per topic: `personen`, `haushalt`, `betreuung`, `anspruch`, `einkommen`, `beitrag` |
| `tests/` | Hand-calculated cases from `challenge/szenarien.md`: `personas.yaml` (P1 to P7b), `grenzfaelle.yaml` (G, X, Q and E cases) |
| `situation_examples/` | Example family P1 for the Web API |

Calculation chain per child and month: entitlement (`kibg_anspruch`), income
(`kibg_massgebendes_einkommen`, `kibg_einkommensfaktor`), maximum rate
(`kibg_hoechstbeitrag`), contribution per hour (`kibg_beitrag_pro_stunde`),
subsidised hours, monthly contribution capped at the costs
(`kibg_beitrag_total`), parents' remaining costs and the shares of canton and
municipality.

The formula of the KiBV annex appears once in the text and therefore once in
the code (`formel_anhang` in `hilfsfunktionen.py`). It is applied where the
text applies it: for B with the municipal supplements Z1 and Z2
(`kibg_beitrag_pro_stunde`) and for the minimum contribution of Art. 6 and
Art. 20 Abs. 1 KiBG without them (`kibg_mindestbeitrag_pro_stunde`).

Sources of the rules: `../challenge/line-to-line-rules.md`. Conventions and
checks: `../RULEBOOK.md`. Decisions: `../docs/CHANGELOG_DECISIONS.md`.

## Required inputs

Without these inputs the text cannot be applied. The model then computes no
amount but stops with an error; the Web API answers with status 400 and names
the missing field (tests F1 to F4 in `tests/test_eingabefehler.py`).

| Input | When required | Why |
|---|---|---|
| `geburtsdatum` | for every child | Minimum age (Art. 4 Abs. 3 KiBG) and maximum rate (Art. 14 KiBV) depend on it |
| `kibg_gesuchstellend` | when two Erziehungsberechtigte live in the household; exactly one of them | Only the applicant must live in the canton (Art. 4 Abs. 1 KiBG, decision O8); the application is made by Erziehungsberechtigte (Art. 9 Abs. 1 KiBG) |

## Provisions not encoded

Line-to-line coding means that every provision is either encoded or listed
here with the reason. Provisions not listed are encoded; the table of encoded
articles in `../docs/CHANGELOG_DECISIONS.md` is generated from the
`reference` of each variable and parameter.

### 1. Computable, but not encoded yet

These rules could be expressed in OpenFisca. They are left out of the first
version because the calculator estimates the contribution for one month and
these rules concern dates and durations of the procedure. Test scenarios are
ready in `../challenge/szenarien.md` (part 6) for the date rules.

| Provision | Content | Why not encoded | Ready scenarios |
|---|---|---|---|
| Art. 9 Abs. 2 KiBG | Retroactive payment if the application is made within 30 days of the start of care, otherwise from the application | Date logic of the procedure; the monthly amount does not change | D1, D2 |
| Art. 25 Abs. 1 and 2 KiBV (draft) | Applications within three months of the start date apply retroactively from the start date | Same as above; only relevant in the transition period | D3 to D7 |
| Art. 6 KiBV (draft) | A facility takes part from the first day of the month after confirmation | Entered as `kibg_einrichtung_angemeldet` for each month instead | D8, D9 |
| Art. 11 Abs. 2 KiBG, Art. 16 Abs. 1 and 2 KiBV (draft) | Duration of the decision: usually 12 months, for school children one school year | Duration of a decision, not the amount | none |
| Art. 11 Abs. 3 KiBV (draft) | New assessment during a running decision applies from the first day of the following month | Date logic; the model compares the income in each month | none |
| Art. 16 Abs. 3 KiBV (draft) | Reductions caused by model changes apply only with the next decision | Matters for reforms, not for one family | none |
| Art. 14 Abs. 4 KiBV (draft), second sentence | At most five care days per week | Inputs are monthly; the weekly spread is unknown (team decision A3, test E1) | E1 |
| Art. 17 KiBG | Total volume of 20 million francs per year; adjustment after three years with a deviation of more than Fr. 500'000 | Needs data on all families in the canton; possible later as a budget simulation | none |

### 2. Deliberately deferred

| Provision | Content | Why deferred |
|---|---|---|
| Art. 13 KiBG, Art. 18 KiBV (draft) | Repayment of contributions received unlawfully, within five years | Concerns a later procedure, not the calculation; whether a payment was unlawful is decided by the municipality (R1 in the rule inventory) |

### 3. Encoded only as inputs (decisions and facts the model does not compute)

| Provision | Content | Input |
|---|---|---|
| Art. 3 Abs. 2 and 3 KiBG, Art. 3 to 5 KiBV (draft) | Recognition and registration of the facility | `kibg_einrichtung_anerkannt`, `kibg_einrichtung_angemeldet` |
| Art. 4 Abs. 2 KiBG, Art. 12 KiBV (draft) | Exception from the minimum employment rate | `kibg_ausnahme_bewilligt` (decision of the municipality), `kibg_ausnahmegrund` (information only) |
| Art. 5 Abs. 3 KiBG, Art. 9 and 10 KiBV (draft) | Relevant income and assets according to Art. 12 and 12bis V EG-KVG (sGS 331.111) | `me_steuerveranlagung`, `me_aktuell`; the V EG-KVG is not part of the challenge material (O5) |
| Art. 7 KiBV (draft) | Only days of actual custody | `betreuungstage_mit_obhut`, `betreuungsstunden` (assumption A5) |
| Art. 20 Abs. 2 KiBG, Art. 24 KiBV (draft) | Supplements of the municipality | `kibg_zusatzbeitrag_z1`, `kibg_zusatzbeitrag_z2`; the amounts differ by municipality and are not public |

### 4. Not computable

Procedure, data protection and administration. They matter for the report
(ethics, data protection), not for the calculation.

| Provision | Content |
|---|---|
| Art. 1 KiBG | Purpose |
| Art. 7 and 8 KiBG, Art. 19 to 23 KiBV (draft) | Electronic platform, data processing, access, logging |
| Art. 10 KiBG | Confirmation of the care relationship by the facility |
| Art. 11 Abs. 1 and 3 KiBG | Decision by the municipal office and its adjustment; the result of the model is an estimate, not a decision |
| Art. 12 Abs. 1 and 3 KiBG, Art. 17 KiBV (draft) | Payment to the facility and to the municipalities (Art. 12 Abs. 2 KiBG is encoded as `kibg_restkosten_eltern`) |
| Art. 14 to 16 KiBG | Duties to cooperate, controlling and monitoring |
| Art. 18 Abs. 2, Art. 19 KiBG | Bound expenditure, costs of implementation |
| Art. 22 and 23 KiBG, Art. 1 KiBV (draft) | Competences and delegation |
| Art. 16 Abs. 4 KiBV (draft) | Reminder before a decision expires |
| Ziff. III KiBG | Repeal of the law of 29 November 2020 (no history before the start date) |

### 5. Out of scope or not regulated in the material

| Provision | Content | Why |
|---|---|---|
| Art. 21 KiBG | Other municipal support beyond this law | Not defined in the text |
| Art. 14 Abs. 5 KiBV (draft) | Care modules and monthly flat rates by guidelines of the Amt für Soziales | The guidelines are not available (O7) |
| Art. 23 lit. f KiBG | Procedure for care in a facility outside the canton | The KiBV draft contains no rule on it |
| Art. 2 KiBV (draft) | Responsible municipality | Entered as `wohngemeinde`; it only matters for the municipal supplements |
| Ziff. IV KiBG, Ziff. IV KiBV (draft) | Start date | Not set; placeholder 2028-08-01 (O1) |

```bash
make test          # run all test cases
make serve-local   # Web API on http://127.0.0.1:5000
```

## Packaging your Country Package for Distribution

Country packages are Python distributions. You can choose to distribute your
package automatically via the predefined continuous deployment system on GitHub
Actions, or manually.

### Automatic continuous deployment on GitHub

This repository is configured with a continuous deployment system to automate
the distribution of your package via `uv`.

#### Setting up continuous deployment

To activate the continuous deployment:

1. Create an account on [PyPI](https://pypi.org/) if you don't already have
   one.
2. Generate a token in your PyPI account. This token will allow GitHub Actions
   to securely upload new versions of your package to PyPI.
3. Add this token to your GitHub repository's secrets under the name
   `PYPI_TOKEN`.

Once set up, changes to the `main` branch will trigger an automated workflow to
build and publish your package to PyPI, making it available for `uv`
installation.

### Manual distribution

If you prefer to manually manage the release and distribution of your package,
follow the guidelines provided by the
[Python Packaging Authority](https://python-packaging-user-guide.readthedocs.io/tutorials/distributing-packages/#packaging-your-project).

This involves detailed steps on preparing your package, creating distribution
files, and uploading them to PyPI.

## Install Instructions for Users and Contributors

This package requires
[Python 3.11](https://www.python.org/downloads/release/python-390/). More
recent versions should work, but are not tested.

All platforms that can execute Python are supported, which includes GNU/Linux,
macOS and Microsoft Windows.

### A. Minimal Installation

Follow this installation if you wish to:

- run calculations on a large population;
- create tax & benefits simulations;
- write an extension to this legislation (e.g. city specific tax & benefits);
- serve your Country Package with the OpenFisca Web API.

For more advanced uses, head to the
[Advanced Installation](#advanced-installation-git-clone).

#### Install this Country Package with [uv](https://docs.astral.sh/uv/)

Install the Country Package:

```sh
uv add install openfisca-ch_sg
```

:tada: This OpenFisca Country Package is now installed and ready!

#### Next Steps

- To learn how to use OpenFisca, follow our
  [tutorials](https://openfisca.org/doc/).
- To serve this Country Package, serve the
  [OpenFisca Web API](#serve-your-country-package-with-the-openFisca-web-api).

Depending on what you want to do with OpenFisca, you may want to install yet
other packages:

- To install extensions or write on top of this Country Package, head to the
  [Extensions documentation](https://openfisca.org/doc/contribute/extensions.html).
- To plot simulation results, try [matplotlib](http://matplotlib.org/).
- To manage data, check out [pandas](http://pandas.pydata.org/).

### B. Advanced Installation (Git Clone)

Follow this tutorial if you wish to:

- create or change this Country Package's legislation;
- contribute to the source code.

#### Clone this Country Package with Git

First, make sure [Git](https://www.git-scm.com/) is installed on your machine.

Set your working directory to the location where you want this OpenFisca
Country Package cloned.

Clone this Country Package on your machine:

```sh
git clone git://github.com/openfisca/openfisca-CH-SG.git
cd openfisca-CH-SG
```

You can make sure that everything is working by running the provided tests with
`make test`.

> [Learn more about tests](https://openfisca.org/doc/coding-the-legislation/writing_yaml_tests.html)

:tada: This OpenFisca Country Package is now installed and ready!

#### Next Steps

- To write new legislation, read the
  [Coding the legislation](https://openfisca.org/doc/coding-the-legislation/index.html)
  section to know how to write legislation.
- To contribute to the code, read our
  [Contribution Guidebook](https://openfisca.org/doc/contribute/index.html).

### C. Contributing

- Read [CONTRIBUTING](CONTRIBUTING.md).
- Open a pull request to the `main` branch of this repository.
- Announce your changes as described in [CONTRIBUTING](CONTRIBUTING.md).

## Serve this Country Package with the OpenFisca Web API

If you are considering building a web application, you can use the packaged
OpenFisca Web API with your Country Package.

To serve the Openfisca Web API locally, run:

```sh
openfisca serve --port 5000 --country-package openfisca_ch_sg
```

Or use the quick-start Make command:

```
make serve-local
```

To read more about the `openfisca serve` command, check out its
[documentation](https://openfisca.org/doc/openfisca-python-api/openfisca_serve.html).

You can make sure that your instance of the API is working by requesting:

```sh
curl "http://localhost:5000/spec"
```

This endpoint returns the [Open API specification](https://www.openapis.org/)
of your API.

:tada: This OpenFisca Country Package is now served by the OpenFisca Web API!
To learn more, go to the
[OpenFisca Web API documentation](https://openfisca.org/doc/openfisca-web-api/index.html).

You can test your new Web API by sending it example JSON data located in the
`situation_examples` folder.

```sh
curl -X POST -H "Content-Type: application/json" \
  -d @./openfisca_ch_sg/situation_examples/couple.json \
  http://localhost:5000/calculate
```
