# Output-Konzept des Rechners

Gilt für das SvelteKit-Interface. Die Punkte unter «Entscheide» hat das Team am
7. November 2026 festgelegt.

**Grundsatz:** OpenFisca liefert nur Werte (Zahlen, ja/nein). Alle Texte liegen
im Interface in `frontend/src/lib/texte.de.json`, damit das Team sie ohne
Code-Änderungen überarbeiten kann. Platzhalter in `{Klammern}` heissen wie die
OpenFisca-Variablen in `challenge/line-to-line-rules.md`. Keine Icons, die
Gestaltung übernimmt das Interface. Ton: höfliche «Sie»-Form, einfache Sätze.

## Fragebogen

Reihenfolge:

1. **Haushalt:** gemeinsamer Haushalt der Erziehungsberechtigten; bei zwei
   Erziehungsberechtigten, wer das Gesuch stellt (`kibg_gesuchstellend`);
   allenfalls Partnerin oder Partner, die oder der nicht erziehungsberechtigt
   ist (Ehe/eingetragene Partnerschaft oder Beginn des gemeinsamen Haushalts).
2. **Pro erziehungsberechtigter Person** (und Partner/in): Wohnsitz im Kanton,
   Beschäftigungsgrad, massgebendes Einkommen und Vermögen gemäss letzter
   Steuerveranlagung; allenfalls Antrag und aktuelles Einkommen
   (Art. 5 Abs. 4 KiBG).
3. **Pro Kind ein Block:** Geburtsdatum, eingeschult (ab Kindergarten, A8),
   Primarschule abgeschlossen, Einrichtungstyp, anerkannt und angemeldet,
   Betreuungsstunden und -tage im Monat, Kosten im Monat.

Nicht abgefragt werden Namen, AHV-Nummer und Adresse (Datenminimierung; die
Plattform nach Art. 21 KiBV braucht sie, der Rechner nicht). Zusatzbeiträge der
Gemeinde (Z1, Z2) werden nicht abgefragt und sind 0.

**Pflichtangaben:** Geburtsdatum jedes Kindes, bei zwei Erziehungsberechtigten
die gesuchstellende Person (OpenFisca meldet sonst Fehler 400 mit dem Feld) und
das massgebende Einkommen. Fehlt eine davon, zeigt das Interface keinen Betrag,
sondern bittet um die Angabe. Beim Einkommen steht der Hinweis: «Diese Zahl
finden Sie auf Ihrer letzten definitiven Steuerveranlagung (Kantons- und
Gemeindesteuern), Art. 5 Abs. 3 KiBG.»

## Ergebnis: fünf Bausteine, pro Kind und als Summe für die Familie

1. **Ergebnis:** Beitrag pro Monat und pro Stunde und die Restkosten der Eltern;
   sonst «voraussichtlich kein Anspruch».
2. **Voraussetzungen:** jede Bedingung (Wohnsitz der gesuchstellenden Person,
   Beschäftigungsgrad nach lit. a und lit. b, Alter des Kindes, Einrichtung)
   als «erfüllt» oder «nicht erfüllt», ein Satz plus Artikel. Es gibt keinen
   dritten Zustand: Die Gemeinde prüft ohnehin jedes Gesuch.
3. **Rechenweg:** Höchstbeitrag, massgebendes Einkommen, Prozentsatz, Beitrag je
   Stunde, Stunden, allenfalls Kostenobergrenze; in Franken und Prozent, nicht
   als Formel.
4. **Hinweise je nach Situation:** Altersgrenze 18 Monate, Neuberechnung ab 25 %
   Einkommensänderung, mögliche Entbindung vom Beschäftigungsgrad, Einkommen der
   Partnerin oder des Partners.

   **Anspruch erfüllt, aber Beitrag Fr. 0:** Wenn `kibg_anspruch` «ja» ist,
   `kibg_hoechstbeitrag` aber 0, gibt es für diese Kombination keinen Ansatz in
   Art. 14 KiBV. Beispiel: schulergänzende Betreuung vor der Einschulung; sie
   setzt die Schulzeit voraus (Teamentscheid). Das Interface zeigt nicht nur
   «Fr. 0», sondern erklärt: «Ihre Familie erfüllt die Voraussetzungen. Für
   schulergänzende Betreuung vor der Einschulung legt Art. 14 der Verordnung
   aber keinen Beitrag fest. Für eine Kita oder Tagesfamilie gäbe es einen
   Beitrag.» Dasselbe gilt sinngemäss, wenn der Beitrag wegen des Einkommens
   0 ist (`kibg_einkommensfaktor` = 0, über Fr. 154'000).
5. **Fester Hinweis (immer):** «Dies ist eine unverbindliche Schätzung.
   Massgebend ist die Verfügung Ihrer Gemeinde, die jedes Gesuch prüft. Die
   Beträge stammen aus dem Entwurf der Verordnung (Vernehmlassung bis
   15. November 2026) und können sich noch ändern. Zusatzbeiträge Ihrer
   Gemeinde sind nicht berücksichtigt; fragen Sie Ihre Gemeinde. Der Rechner
   speichert Ihre Angaben nicht; sie werden nur für die Berechnung verwendet.»
   Der stärkere Satz «es werden keine Angaben gespeichert» kommt erst, wenn
   geklärt ist, wo die OpenFisca-API läuft und ob sie Anfragen protokolliert.

Ermessensentscheide (Art. 4 Abs. 2 KiBG, Art. 12 KiBV) trifft der Rechner nie;
er verweist an die zuständige Stelle der Gemeinde.

## Entscheide (Punkte 7 bis 13)

| Nr. | Frage | Entscheid |
|---|---|---|
| 7 | Dritter Zustand «von der Gemeinde zu prüfen» | Nein. Zwei Zustände; die Gemeinde prüft jedes Gesuch, das sagt der feste Hinweis |
| 8 | Fehlendes massgebendes Einkommen | Pflichtangabe; keine Spanne |
| 9 | Hilfe beim Einkommen | Hinweis auf die letzte definitive Steuerveranlagung; keine eigene Schätzung |
| 10 | Zusatzbeiträge Z1, Z2 | Nicht abgefragt, 0, mit Hinweis |
| 11 | Datenschutz-Satz | Vorsichtige Formulierung, Datenminimierung im Fragebogen |
| 12 | Aufbau des Fragebogens | Haushalt, dann Personen, dann pro Kind ein Block; Ergebnis pro Kind und Summe |
| 13 | Ton und Ablage | «Sie»-Form; `frontend/src/lib/texte.de.json` |
