// challenge description
Context and overall challenge
This challenge starts with St. Gallen’s revised legislation on contributions for family- and school-based childcare (KiBG) and its implementing ordinance. The reform aims to create a more consistent system of financial support focused on reducing parents’ childcare costs. Participants will use the cantonal implementation materials as their starting point.

The law is linked here: https://www.sg.ch/gesundheit-soziales/soziales/kinder-und-jugendliche/kindertagesbetreuung/kinderbetreuungsgesetz/umsetzung-der-kibg-revision.html

The Ordinance is linked here: https://www.sg.ch/news/sgch_allgemein/2026/10/verordnung-familien--und-schulergaenzende-kinderbetreuung.html

OpenFisca is an open-source engine for modeling tax and benefit rules as code. It allows developers, legal experts, and researchers to work with a shared model that can support calculators, public-facing services, and policy simulations. Examples include French benefits services such as Mes droits sociaux and New Zealand’s Rapu Ture, an interface for exploring encoded legal rules. To this end, the system is particularly suited to the kind of modeling this tool demands.

The overall challenge is to encode a selected part of these rules in OpenFisca and make it understandable to the people who need it. Teams should identify the legal versions they use and distinguish rules currently in force from other rules.

Teams may choose either of the following sub-challenges or combine them.

Sub-challenge 1 — Access to justice: Build a childcare support calculator
For participants with a stronger technical focus
Build a working prototype that helps a fictional family assess whether it could qualify for childcare support and, where feasible, estimate the amount. Start with the OpenFisca Country Template and create a small Swiss model focused on St. Gallen childcare support.

Ideally, your prototype will:

Encode a clearly defined subset of eligibility or calculation rules, with references to relevant legal provisions.
Collect the information needed for that subset through a simple questionnaire, or take the opportunity to design a more creative and engaging user experience.
Design intuitive ways to explain the result to the user, clearly showing which facts and rules determined the outcome.
Develop methods to handle missing information and flag situations requiring further assessment.
Sub-challenge 2 — Legal design: Make the encoded rules readable and reviewable
For participants with a stronger legal focus
Develop a legally grounded representation of the childcare support rules that families can understand and developers can implement/review. Choose a manageable set of provisions from the KiBG and the relevant ordinance materials. Map their conditions, exceptions, and dependencies, then show how these should be represented in an OpenFisca model.

Your prototype should:

Translate selected provisions into a structured specification (e.g., decision tree or rule table).
Link each rule to its legal source and distinguish legislation, explanatory guidance, and assumptions.
Identify ambiguities, unresolved questions, and decisions that require human judgment.
Take an example situation and explain, in plain language, what the model predicts.
