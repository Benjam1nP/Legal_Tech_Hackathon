# KiBG Calculator St. Gallen

**Rules as Code for the new childcare contributions in the Canton of St. Gallen**

Team Ctrl+Alt+Elite: Karla Ruggaber, Benjamin Pfister, Rea Graf, Julian Böhi
Legal Hackathon 2026, challenge "Making childcare support understandable with OpenFisca" (Law & Tech Entrepreneurs, University of St. Gallen)

Parents in St. Gallen who need childcare all have the same three questions: Do we get money? How much? And why? The new childcare law (KiBG) and its draft ordinance (KiBV) contain the answers, but spread over fifteen pages, a formula with six variables and a 30-day deadline. We wrote the rules of both texts in OpenFisca, line by line, and checked them with tests that we calculated by hand. On top of this model we built a website that asks a family a few questions and explains the result with the relevant articles.

Example: the Keller family (parents working 100 % and 40 %, relevant income Fr. 97'000, a one-year-old in a Kita for 80 hours a month at Fr. 1'040) receives **Fr. 440 per month**. Canton and municipality each pay half, and the parents still pay Fr. 600.

![Result for the Keller family](docs/screenshots/02_rechner_ergebnis.png)

This README gives a short overview. The full legal and technical report, with all details, the complete reasoning behind our assumptions and screenshots of every tab, is in [`docs/KiBG-Calculator_Report.md`](docs/KiBG-Calculator_Report.md) (also as a [Word file](docs/KiBG-Calculator_Report.docx)).

## Contents

1. [The problem](#1-the-problem)
2. [Our solution](#2-our-solution)
3. [Legal basis and scope](#3-legal-basis-and-scope)
4. [How it works](#4-how-it-works)
5. [Getting started](#5-getting-started)
6. [Tests and checks](#6-tests-and-checks)
7. [Repository structure](#7-repository-structure)
8. [From law to code](#8-from-law-to-code)
9. [Responsible design](#9-responsible-design)
10. [Limitations and next steps](#10-limitations-and-next-steps)
11. [Team, AI use and open source](#11-team-ai-use-and-open-source)
12. [Further documentation](#12-further-documentation)

## 1. The problem

Legal rules are rarely written with the people they affect in mind. They are spread over several acts, refer to one another constantly and use terms that mostly make sense to lawyers.

The new childcare law of St. Gallen shows this well. On 14 June 2026 the voters accepted the fully revised KiBG with 57.8 % yes. The principle is straightforward: instead of lump sums to the municipalities, families receive a contribution per child and per hour of care, calculated the same way across the canton. The details are another matter. They are in the ordinance (KiBV), which is still a draft and open for consultation until 15 November 2026. The new system is planned to start in 2028.

For parents, applying these rules is hard. Whether they are entitled at all depends on how much both of them work, where they live, the age of the child and the type of care. The amount then depends on the "massgebendes Einkommen", which is defined in yet another ordinance, on seven different hourly rates and on a formula in the annex of the KiBV. One detail is easy to miss and costly: if the application is filed more than 30 days after care begins, the first weeks are not paid. Few parents will work through fifteen pages of legal text to find this out.

This is the situation our tool is built for. A family is about to apply, or is still deciding whether to take a Kita place. Before committing, they want to know whether they are entitled, how much they will receive and why, and what they need to do next.

## 2. Our solution

The project is built on the idea of Rules as Code. The legal rules are written down a second time as program code, next to the text, so that people can read them, software can run them and tests can check them. Once the rules are encoded and tested, other applications can use the same model without rebuilding the law. Our website is one of them. A municipality's case software, a budget simulation for the canton or a French version of the website could be others, and they would all give the same answer. When the law changes, the rules change in one place and the tests show right away whether everything still fits.

The website (in German) has four tabs:

| Tab | What it does |
|---|---|
| Rechner | Questionnaire for one family. Shows the expected contribution per child and month, what the parents still pay, each condition with its article, the calculation in francs and hints on what to do next |
| Vergleichstool | "Does working more pay off?" Parents mark their working half-days in a weekly grid. The tool varies one parent's workload, compares Kita, Tagesfamilie and after-school care, and shows what is left of the extra wage after childcare (before tax) |
| Überblick | The way to the contribution in six steps: what parents do, what happens without them, and the 30-day deadline on a timeline |
| Gesetzgebung | Full text of the KiBG and the KiBV draft. Every article reference on the site jumps to the exact paragraph |

The main users are families before they apply. Municipalities could use the same model to check applications and explain their decisions, and the canton could use it in the consultation and later for budget simulations (Art. 17 KiBG).

## 3. Legal basis and scope

| Act | Version we used | Status (8 Nov 2026) |
|---|---|---|
| KiBG (Gesetz über Beiträge für familien- und schulergänzende Kinderbetreuung) | [`challenge/Gesetz.pdf`](challenge/Gesetz.pdf), text after the first reading of 16 Sept 2025 | Adopted 14 June 2026, start date not set yet |
| KiBV (Verordnung) | [`challenge/Verordnung.pdf`](challenge/Verordnung.pdf), RRB 2026/733 | Draft, consultation until 15 Nov 2026 |

Since nothing is in force yet, we use **1 August 2028** as a placeholder start date, since this is the current planned start date. Every reference to the ordinance in the code says "(Entwurf)". Where the text is unclear or silent, we mark our own choices:

- **Law / ordinance (draft):** the text says so.
- **Interpretation (O1–O12):** the wording allows more than one reading, and we chose one with reasons.
- **Assumption (A1–A12):** the text says nothing, so we filled the gap ourselves.
- **Discretion:** a person at the municipality decides. In the model this is always an input, never a formula.

We went through every article, paragraph and letter of both acts and put each one into one of four groups. The full list is in the rule inventory [`challenge/line-to-line-rules.md`](challenge/line-to-line-rules.md).

| Group | Examples |
|---|---|
| Encoded as rules | Entitlement (Art. 3–4 KiBG), income (Art. 5 KiBG, Art. 8 and 11 KiBV), rates and formula (Art. 13–15 KiBV, annex), hour and cost caps, split between canton and municipality, start of contributions (Art. 9 KiBG, Art. 6 and 25 KiBV), length of a decision (Art. 11 KiBG, Art. 16 KiBV) |
| Only an input | Recognition of the facility, exception from the minimum workload, the relevant income itself, municipal supplements Z1 and Z2 |
| Not encoded yet | Recalculation during a decision (Art. 11 Abs. 3 KiBV), the five-days-a-week limit, the budget of Art. 17 KiBG, repayment (Art. 13 KiBG) |
| Not computable | Platform, data protection, payment flows, duties to cooperate |

## 4. How it works

```
SvelteKit website  ── POST /calculate ──▶  OpenFisca Web API
(questions, texts,  ◀── numbers, yes/no ──  (model: entities, parameters,
 explanations)                               variables, 125 tests)
```

All legal logic lives in the OpenFisca model. The website builds an OpenFisca "situation" from the form on its server, sends it to `/calculate` and turns the numbers it gets back into sentences. Nothing is stored.

For each child and month the model goes through these steps:

1. **Entitlement:** the applicant lives in the canton, each parent works at least 20 % and, in a shared household, both together at least 120 % (or the municipality granted an exception), the child is between 3 months old and the end of primary school, and the facility is recognised and registered.
2. **Relevant income:** both parents' incomes in a shared household; with separated parents the applicant's income plus that of a partner in a "gefestigte Lebensgemeinschaft".
3. **Maximum rate per hour** by age and type of care (Fr. 11.00 for a Kita under 18 months, then Fr. 7.50, and so on).
4. **Contribution per hour:** maximum rate × income factor. The factor is 1 up to Fr. 40'000 and drops in a straight line to 0 at Fr. 154'000.
5. **Subsidised hours:** at most 12 per care day.
6. **Cost cap:** never more than the actual costs.
7. **Split:** canton and municipality pay half each; the parents pay the rest.

The Keller family step by step:

| Step | Calculation | Result |
|---|---|---|
| Income | 60'000 + 37'000 | Fr. 97'000 |
| Income factor | 1 − (97'000 − 40'000) / 114'000 | 0.5 |
| Rate | Kita, under 18 months | Fr. 11.00 |
| Per hour | 11.00 × 0.5 | Fr. 5.50 |
| Per month | 5.50 × 80 hours | **Fr. 440** |
| Parents pay | 1'040 − 440 | **Fr. 600** |

The model has 65 variables (37 formulas and 28 inputs) and 23 parameters. Each one carries the article it comes from.

**Missing or impossible information.** Some answers are needed to apply the law at all: the child's date of birth, the start of care, the application date and the relevant income. If one of them is missing, the model stops with an error that names the field, and the website asks for the answer instead of showing an amount. Impossible combinations, such as care hours without care days or a baby marked as being at school, stop the calculation in the same way. Decisions that belong to the authorities, like an exception from the minimum workload or the recognition of a facility, are always asked as inputs and never guessed.

## 5. Getting started

You need `git`, `bash`, [uv](https://docs.astral.sh/uv/) and Node.js 22. These are the versions we used:

| Tool | Purpose | Version |
|---|---|---|
| OpenFisca Core (with Web API) | Rules engine and API | 44.7.1 |
| Python | Model | 3.9 or later (tested with 3.10) |
| SvelteKit, Svelte, Vite | Website | 3.1, 5.57, 8.3 |
| marked, marked-footnote | Rendering the legal texts | 18.1.1, 1.4.0 |
| ruff, yamllint, pre-commit | Automated checks | 0.16.8, 1.38.0, 4.6.2 |
| Node.js | Website and website tests | 22 |

```bash
# once: installs OpenFisca, the checks and the git hooks
bash tools/setup.sh

# terminal 1: OpenFisca Web API on http://127.0.0.1:5000
cd openfisca-CH-SG && make serve-local

# terminal 2: website on http://localhost:5173
cd frontend && npm install && npm run dev
```

On macOS, port 5000 is often taken by AirPlay. In that case start the API on another port and tell the website where it is:

```bash
cd openfisca-CH-SG && uv run openfisca serve --country-package openfisca_ch_sg --port 5001
cd frontend && OPENFISCA_URL=http://127.0.0.1:5001 npm run dev
```

You can also ask the API directly with the Keller family:

```bash
curl -X POST -H "Content-Type: application/json" \
  -d @openfisca-CH-SG/openfisca_ch_sg/situation_examples/p1_paar_kita.json \
  http://127.0.0.1:5000/calculate
```

## 6. Tests and checks

```bash
cd openfisca-CH-SG && make test     # 125 OpenFisca tests
cd frontend && npm test             # 27 website tests (14 of them need the API running)
```

We calculated the expected amounts by hand from the law before writing the code, so the tests check the code against the law and not against itself. The cases come from the scenario catalogue [`challenge/szenarien.md`](challenge/szenarien.md):

| File | Content |
|---|---|
| `tests/personas.yaml` | Seven example families (P1–P7b) |
| `tests/grenzfaelle.yaml` | Boundary cases, cases without entitlement, interpretation cases, known limits |
| `tests/datumsregeln.yaml` | Start of contributions, facility participation, length of a decision |
| `tests/test_eingabefehler.py` | Inputs that must stop the calculation, e.g. a missing date of birth |
| `tests/test_vollzugsbeginn.py` | The placeholder start date is the same everywhere |

On every commit `ruff` and `yamllint` run; on every push also all OpenFisca tests and our own checker (`tools/check_openfisca.py`). The checker warns, for example, when a rule has no article reference or a KiBV reference lacks "(Entwurf)". GitHub Actions runs the same checks again. All tests passed on 8 November 2026 (OpenFisca Core 44.7.1, Node 22).

## 7. Repository structure

```
challenge/            challenge material: KiBG, KiBV draft, pitch,
                      rule inventory (line-to-line-rules.md), scenario catalogue (szenarien.md)
openfisca-CH-SG/      the OpenFisca model
  openfisca_ch_sg/
    entities.py       household with parents, children and partner
    parameters/kibg/  all values from the text, each with its article
    variables/        inputs and formulas, one file per topic
    tests/            hand-calculated test cases
frontend/             SvelteKit website
  src/lib/texte.de.json   all texts of the calculator, editable without code
  src/lib/recht/          KiBG and KiBV as Markdown with an anchor per paragraph
docs/                 decision log, legal design document, output concept
tools/                setup script, rulebook checker, decision-log generator
RULEBOOK.md           how we write the rules in code and what is checked
```

## 8. From law to code

**One provision, one element.** We followed OpenFisca's "line-to-line" principle: each condition or value in the text is its own variable or parameter, named with the German legal term and referenced to its article. Where the law states the same rule twice (the cost cap in Art. 6 Abs. 2 and Art. 20 Abs. 3 KiBG), the code does too. Lawyers on the team could put the code next to the text and tick off each line.

**Our process:**

1. Read KiBG and KiBV in full and narrow the focus to what affects a family: entitlement, amount and deadlines.
2. Assign every paragraph to an OpenFisca building block in the rule inventory, or mark it as input only or not encoded, with a reason.
3. Decide openly where the text is unclear (interpretations O) or silent (assumptions A).
4. Calculate example families and edge cases by hand. These became the tests.
5. Write the model in OpenFisca.
6. Build the website that asks the questions and explains the answer.
7. Check code and texts against the law once more. Every decision is in a commit message and ends up in the decision log.

**Interpretations and assumptions.** An interpretation (O) was needed where the wording allows more than one reading; we chose one and gave reasons. An assumption (A) was needed where the text says nothing; we filled the gap ourselves. Each one is a test case. The reasoning is in the rule inventory (O) and the scenario catalogue (A).

| No. | Question | Our decision |
|---|---|---|
| O1 | Start date not set ("ab ●●") | Placeholder 1 August 2028 |
| O2 | A child of exactly 18 months is neither "under" nor "over" 18 months | Higher rate for the full first 18 months |
| O3 | Is 120 % together enough if one parent works less than 20 %? | No, lit. a and b apply together: each parent at least 20 % |
| O4 | Does "no contribution above Fr. 154'000" also apply to the supplement Z2? | No, Z2 is income-independent and still paid |
| O5 | Relevant income is defined in the V EG-KVG, which we don't have | Entered by the user |
| O6 | Our law PDF is the first-reading text | Open, to be checked against the adopted text |
| O7 | How does "5 days per week" work with monthly figures? | Hours per month are entered; the 5-day limit is not checked |
| O8 | Which parent must live in the canton if they are separated? | The applicant; the applicant's municipality is responsible |
| O9 | When does the school year start? | 1 August |
| O10 | Alternating custody: who applies? | Each parent for their own custody days |
| O11 | Which rate for private special schools? | The rate of the form of care (after-school care) |
| O12 | Does the 25 % income change also count upwards? | Yes, in both directions |

O3 has the biggest effect. Without it, a couple with 120 % and 0 % would be entitled. We read both letters together because the wording requires each parent to work, because 120 % builds on the 20 % minimum, because couples should not face a lower threshold than single parents (Art. 8 BV), and because a parent who does not work at all can usually look after the child.

| No. | Assumption |
|---|---|
| A1 | Age of the child and length of a partnership are determined on the first day of the month |
| A2 | If minimum contribution and municipal supplement together exceed the costs, the supplement is cut first |
| A3 | The limit of five care days per week is not checked |
| A4 | Monthly amounts are rounded to 5 Rappen; the hourly rate is not rounded; the cost cap applies after rounding |
| A5 | Parents only enter days and hours with actual custody |
| A6 | Each parent works at least 20 %, and parents in a shared household at least 120 % together (see O3) |
| A7 | A deadline in days starts the day after the event; a deadline in months ends on the day with the same number |
| A8 | A child counts as enrolled in school from entry into compulsory kindergarten |
| A9 | In the month contributions start, only care days and hours from that date are entered |
| A10 | The application date is the day it is handed in at the municipality or posted |
| A11 | The decision starts when the contributions start (provisional) |
| A12 | If a decision ends mid-month, only care days up to that date are entered (provisional) |

**Discretion stays with people.** Whether a family gets an exception from the minimum workload, whether a facility is recognised and what the relevant income is are decided by authorities. The calculator asks for them and never guesses.

**What we found in the texts.** Coding the rules showed us 24 places where the law or the draft is unclear or inconsistent. Seven of them matter most for families, and each could be fixed with one sentence in the ordinance:

| No. | Provision | Issue | Effect (example) |
|---|---|---|---|
| U11 | Art. 5 Abs. 4 KiBG / Art. 11 KiBV | Law: current income counts if it changed a lot. Ordinance: only on request | Fr. 725.60 instead of Fr. 416.85 per month if income rose and nobody asks |
| U15 | Art. 11 KiBG, Art. 16 KiBV | Does the rate drop during a decision when the child turns 18 months? | Up to Fr. 140 per month |
| U17 | Art. 9 Abs. 2 KiBG | Which start of care counts for follow-up applications? | Fr. 450 lost in our example |
| U13, U14 | Art. 6 KiBG, Art. 14 KiBV | Do meals count as costs? Booked or attended hours? | Fr. 1'100 vs. 1'000; Fr. 440 vs. 330 |
| U2 | Art. 23 lit. f KiBG | No rule for care outside the canton | After-school care across the border hardly possible |
| U7 | Art. 8 KiBV | Single parent without a second parent: does a partner's income count? | Fr. 270 vs. Fr. 486 |
| U9 | Art. 4 Abs. 2 KiBG / Art. 12 KiBV | Ordinance allows exceptions for people without any job, the law does not clearly | Fr. 594 vs. nothing |

The full list with examples is in Part 7 of the scenario catalogue. We think these points are worth submitting in the consultation.

## 9. Responsible design

**Data.** The calculator asks only what the calculation needs: no names (children are "Kind 1", "Kind 2"), no address, no AHV number. Nothing is stored. We did not promise that no data is stored anywhere, because that depends on where the API will be hosted and what its server logs.

**No chatbot.** We thought about adding a chatbot for follow-up questions and decided against it. The data a family enters is sensitive: income, work, separation, custody, sometimes the reason for an exception. A useful chatbot would need this data and would send it to an external AI provider. We did not want that, and we don't think users would either.

**Security and accountability.** No login, no accounts, no database. The OpenFisca API is only called from the website's server, and wrong or impossible inputs stop the calculation instead of producing a number. The binding decision stays with the municipality (Art. 11 KiBG), and every result says so. Every rule has its article and every decision its reason and author in the decision log.

**Transparency.** The legal status is visible (draft ordinance, placeholder start date), every result shows its conditions and calculation, and the article links lead to the exact paragraph.

**Fairness.** We checked whether our simplifications put certain groups at a disadvantage. Where the text leaves a group unclear, such as single parents without a second parent (U7), we raise the question openly instead of quietly choosing the reading that pays less. The website uses plain language and polite "Sie". The 30-day deadline, the rule most likely to cost a family money without anyone noticing, is shown in the result and on a timeline in the overview. When the calculator says "no", it names the condition that failed, and if it is the workload, it points to the exception the municipality can grant.

**Known limits.** The five-days-a-week limit is not checked, the reference date for the child's age is the first of the month, the income is typed in by the family, one form of care per child and month, and all amounts may change after the consultation.

## 10. Limitations and next steps

Open points:

- The law PDF is the first-reading text. It has to be compared with the adopted version of 14 June 2026.
- Hosting, logging and a security review are still missing.
- Once the start date is set, it has to be changed in three places in the code (a test checks that they match).
- Once the ordinance (KiBV) is adopted after the consultation, the rules in the model have to be adapted to whatever has changed compared with the draft. Since every value is a parameter with its article and every rule has its tests, the changes can be made in one place and checked right away.

Possible extensions:

- Municipal supplements Z1 and Z2 per municipality
- Relevant income calculated from tax data
- Budget simulation for the 20 million francs of Art. 17 KiBG
- Recalculation during a running decision
- English, French and Italian versions of the website. All texts are in separate files, so the model would not change.

## 11. Team, AI use and open source

| Member | Main contributions |
|---|---|
| Karla Ruggaber | Rule inventory and scenario catalogue incl. unclear provisions, interpretation decisions, date rules, comparison tool, legislation tab, frontend tests |
| Benjamin Pfister | Rulebook, checker and automated checks, core model, duration of decisions, tests from the catalogue, output concept, calculator interface and design |
| Rea Graf | [to be completed] Assumptions A1–A12 and their legal reasoning, … |
| Julian Böhi | [to be completed] |

**Statement of Author Contribution and AI Use.** All four of us are responsible for the whole project and can explain every part of it, including the parts where AI was used. We used one AI tool, Claude (Anthropic), mostly as Claude Code inside the repository. Every single use is recorded in the commit messages and listed in Section 6 of [`docs/CHANGELOG_DECISIONS.md`](docs/CHANGELOG_DECISIONS.md). In summary:

| Purpose | Specific uses |
|---|---|
| Setting up tooling | Drafted the rulebook, the rulebook checker, the decision-log generator, the git hooks and the GitHub workflows, following our instructions |
| Writing code from our legal specification | Wrote `entities.py`, the parameter files and the variables from our rule inventory; applied renames; split merged provisions after our line-to-line review; encoded the date rules and the duration of decisions |
| Tests | Converted our hand-calculated scenarios into OpenFisca tests; added input-error tests; checked rounding with a sweep of values |
| Reviewing code against the text | Compared Art. 5, 8 and 11 with the wording and flagged deviations, which we then decided on |
| Options for decisions | Prepared options for the output concept (points 7 to 13); the team chose |
| Texts and interface | Drafted the interface texts from our output concept (then revised by the team); drafted the legal design document from our rule inventory and scenarios (checked by the team); built the SvelteKit interface and the overview tab from the team's content; tested pages in a headless browser |
| Full report | Drafted the full report in English from our repository, decision log, rule inventory and scenario catalogue; the team then reviewed and edited it |
| This README | Drafted this README from the report and the repository; the team then reviewed and edited it |

The legal analysis is our own work: the classification of every provision in the rule inventory, the hand calculations in the scenario catalogue, all interpretations (O1–O12) and assumptions (A1–A12), and the list of unclear provisions. Where the AI proposed an interpretation, it was marked as provisional and only became final after a team decision. Code was only accepted when it passed the tests, and the expected values in those tests were calculated by hand before the code existed.

**Open source and external resources:**

| Resource | Use | Licence |
|---|---|---|
| OpenFisca Country Template, OpenFisca Core | Model and Web API | AGPL-3.0 |
| SvelteKit, Svelte, Vite | Website | MIT |
| marked, marked-footnote | Rendering the legal texts | MIT |
| Geist, Geist Mono | Typeface | SIL Open Font License |
| uv, ruff, yamllint, pre-commit | Environment and checks | Open source |
| Photo of St. Gallen (Home tab) | Decoration | [source to be added] |
| KiBG, KiBV draft, pitch, OpenFisca introduction | Challenge material | Canton of St. Gallen, legalhackathons.org |

## 12. Further documentation

The most complete document is the full report. The other files are the working documents we built the project with.

| File | Content |
|---|---|
| [`docs/KiBG-Calculator_Report.md`](docs/KiBG-Calculator_Report.md) ([Word](docs/KiBG-Calculator_Report.docx)) | Full legal and technical report: problem, process, model, legal reasoning, responsible design, the full reasoning for assumptions A1–A12, screenshots of the Keller family |
| [`challenge/line-to-line-rules.md`](challenge/line-to-line-rules.md) | Rule inventory: every provision assigned to code, interpretations O1–O12 |
| [`challenge/szenarien.md`](challenge/szenarien.md) | Scenario catalogue with hand calculations, assumptions A1–A12, unclear provisions U1–U24 |
| [`docs/CHANGELOG_DECISIONS.md`](docs/CHANGELOG_DECISIONS.md) | All decisions with reason, source and author; table of encoded articles; AI use |
| [`docs/legal-design.md`](docs/legal-design.md) | Plain-language explanation for families with decision tree and the Keller example |
| [`docs/output-konzept.md`](docs/output-konzept.md) | How the calculator presents its result |
| [`RULEBOOK.md`](RULEBOOK.md) | Coding conventions and automated checks |
| [`openfisca-CH-SG/README.md`](openfisca-CH-SG/README.md) | The model in detail, including the provisions that are not encoded |
| [`frontend/README.md`](frontend/README.md) | The website in detail |

## Licence

The OpenFisca model is based on the OpenFisca Country Template and licensed under AGPL-3.0 (see [`openfisca-CH-SG/LICENSE`](openfisca-CH-SG/LICENSE)).
