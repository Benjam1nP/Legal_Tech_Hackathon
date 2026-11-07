# Output-Konzept des Rechners (Entwurf)

Entwurf zur gemeinsamen Überarbeitung. Gilt für das SvelteKit-Interface.

**Grundsatz:** OpenFisca liefert nur Werte (Zahlen, ja/nein). Alle Texte liegen
im Interface (z. B. `texte.de.json`), damit das Team sie ohne Code-Änderungen
überarbeiten kann. Platzhalter in `{Klammern}` heissen wie die
OpenFisca-Variablen in `challenge/line-to-line-rules.md`. Keine Icons, die
Gestaltung übernimmt das Interface.

Jedes Ergebnis besteht aus fünf Bausteinen:

1. **Ergebnis:** Beitrag pro Monat und pro Stunde; sonst «voraussichtlich kein
   Anspruch». Fehlt eine Pflichtangabe (Geburtsdatum eines Kindes; bei zwei
   Erziehungsberechtigten die Angabe, wer das Gesuch stellt), rechnet
   OpenFisca nicht und meldet einen Fehler (Status 400, mit dem fehlenden
   Feld). Das Interface zeigt dann keinen Betrag, sondern bittet um die
   fehlende Angabe.
2. **Voraussetzungen:** jede Bedingung (Wohnsitz, Beschäftigungsgrad, Alter des
   Kindes, Einrichtung) als «erfüllt» / «nicht erfüllt», ein Satz plus Artikel.
3. **Rechenweg:** Höchstbeitrag, massgebendes Einkommen, Prozentsatz, Beitrag je
   Stunde, Stunden, allenfalls Kostenobergrenze; in Franken und Prozent, nicht
   als Formel.
4. **Hinweise je nach Situation:** Altersgrenze 18 Monate, Neuberechnung ab 25 %
   Einkommensänderung, mögliche Entbindung vom Beschäftigungsgrad, Einkommen der
   Partnerin oder des Partners.

   **Anspruch erfüllt, aber Beitrag Fr. 0:** Wenn `kibg_anspruch` «ja» ist,
   `kibg_hoechstbeitrag` aber 0, gibt es für diese Kombination von Alter und
   Betreuungsform keinen Ansatz in Art. 14 KiBV (Beispiel: schulergänzende
   Betreuung vor der Einschulung). Das Interface darf dann nicht nur «Fr. 0»
   zeigen, sondern erklärt: «Ihre Familie erfüllt die Voraussetzungen. Für
   schulergänzende Betreuung vor der Einschulung legt Art. 14 der Verordnung
   aber keinen Beitrag fest. Für eine Kita oder Tagesfamilie gäbe es einen
   Beitrag.» Dasselbe gilt sinngemäss, wenn der Beitrag wegen des Einkommens
   0 ist (`kibg_einkommensfaktor` = 0, über Fr. 154'000).
5. **Fester Hinweis:** unverbindliche Schätzung, massgebend ist die Verfügung der
   Gemeinde; Beträge aus dem Verordnungsentwurf; Zusatzbeiträge der Gemeinde
   nicht berücksichtigt; keine Angaben gespeichert.

Ermessensentscheide (Art. 4 Abs. 2 KiBG, Art. 12 KiBV) trifft der Rechner nie;
er verweist an die zuständige Stelle der Gemeinde.
