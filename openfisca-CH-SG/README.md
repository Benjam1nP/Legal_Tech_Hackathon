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

Sources of the rules: `../challenge/line-to-line-rules.md`. Conventions and
checks: `../RULEBOOK.md`. Decisions: `../docs/CHANGELOG_DECISIONS.md`.

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
