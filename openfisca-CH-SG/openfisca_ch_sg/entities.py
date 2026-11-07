"""Entities of the KiBG model.

Who the rules apply to, in the terms of the text:

- Person: every individual (Erziehungsberechtigte, Kind, Partnerin/Partner).
- Household: the household of the applicant, with the roles
  erziehungsberechtigt (Art. 2 Abs. 1 KiBG), kind (Art. 4 Abs. 3 KiBG) and
  partner (Art. 8 Abs. 1 lit. b KiBV, Entwurf).

Modelling convention (see RULEBOOK.md and docs/CHANGELOG_DECISIONS.md): a
household is the household of the applicant. In a gemeinsamer Haushalt both
Erziehungsberechtigte are members. With separated parents only the applicant
is erziehungsberechtigt in the household; the other parent applies separately
for their own days of custody (Art. 7 KiBV, Entwurf).

See https://openfisca.org/doc/key-concepts/person,_entities,_role.html
"""

from openfisca_core.entities import build_entity

Household = build_entity(
    key="household",
    plural="households",
    label="Haushalt der gesuchstellenden Person",
    doc="""
    Haushalt der gesuchstellenden erziehungsberechtigten Person.

    Rollen:
    - erziehungsberechtigt: Personen, die für ein Kind in ihrer Obhut Beiträge
      geltend machen (Art. 2 Abs. 1 KiBG). Höchstens zwei, und nur beide,
      wenn sie einen gemeinsamen Haushalt führen.
    - kind: die betreuten Kinder (Art. 4 Abs. 3 KiBG).
    - partner: Partnerin oder Partner im gleichen Haushalt, die oder der
      gegenüber dem Kind nicht erziehungsberechtigt ist
      (Art. 8 Abs. 1 lit. b KiBV, Entwurf).
    """,
    roles=[
        {
            "key": "erziehungsberechtigt",
            "plural": "erziehungsberechtigte",
            "label": "Erziehungsberechtigte",
            "max": 2,
            "doc": "Erziehungsberechtigte nach Art. 2 Abs. 1 KiBG.",
        },
        {
            "key": "kind",
            "plural": "kinder",
            "label": "Kind",
            "doc": "Betreute Kinder nach Art. 4 Abs. 3 KiBG.",
        },
        {
            "key": "partner",
            "label": "Partnerin oder Partner (nicht erziehungsberechtigt)",
            "max": 1,
            "doc": "Partnerin oder Partner nach Art. 8 Abs. 1 lit. b KiBV (Entwurf).",
        },
    ],
)

Person = build_entity(
    key="person",
    plural="persons",
    label="Person",
    doc="""
    Eine einzelne Person: erziehungsberechtigte Person, Kind oder Partnerin
    bzw. Partner. Der Beitrag wird pro Kind berechnet.
    """,
    is_person=True,
)

entities = [Household, Person]
