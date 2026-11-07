# Regelinventar KiBG / KiBV (Zeile für Zeile)

Jede Bestimmung des Gesetzes (KiBG, `Gesetz.pdf`) und der Verordnung (KiBV, `Verordnung.pdf`, Entwurf) ist hier einem der vier OpenFisca-Konzepte zugeordnet: **Periode**, **Parameter**, **Entität**, **Variable**.

**Legende**

- **Nicht berechenbar:** Verfahren, Datenschutz, Finanzverwaltung. Gehört in die Dokumentation, nicht in den Code.
- **Ausserhalb des Umfangs:** grundsätzlich berechenbar, aber nicht Teil der Berechnung für eine Familie.
- **Zurückgestellt (R1, R2 …):** relevant, wird aber anfangs bewusst nicht modelliert. Details im Abschnitt «Zurückgestellt, aber relevant».
- Variablen sind entweder **Eingaben** (Tatsachen oder menschliche Entscheide, welche die Nutzerin oder der Nutzer eingibt) oder **Formeln** (von OpenFisca berechnet).
- **Namen (festgelegt):** Formeln und Parameter immer mit `kibg_` bzw. `kibg.`. Eingaben ohne Präfix nur, wenn sie eine allgemeine Tatsache sind (`geburtsdatum`, `beschaeftigungsgrad`); Begriffe, die KiBG/KiBV selbst schaffen, mit `kibg_`.
- **O1, O2 …** verweisen auf die offenen Fragen am Schluss.
- **Periode:** Alle Parameter gelten ab Vollzugsbeginn, der noch nicht feststeht; Platzhalter **2028-08-01** (O1). Die Periode jeder Variable steht im Abschnitt «Variablen: Entität und Periode».

---

## Entitäten (Struktur)

| Entität / Rolle | Quelle | Bemerkung |
|---|---|---|
| `Person` | — | Einzelpersonen: Eltern, Partner/in, Kind |
| `Household`, Rolle `erziehungsberechtigt` (max. 2) | KiBG 2.1 | Personen, die das Kind in Obhut haben und Beiträge geltend machen |
| `Household`, Rolle `partner` (max. 1) | KiBV 8.1b | Partner/in in gefestigter Lebensgemeinschaft, die **nicht** erziehungsberechtigt ist. Diese Rolle fehlt in der Vorlage noch |
| `Household`, Rolle `kind` (beliebig viele) | KiBG 4.3 | Die betreuten Kinder |

---

## Variablen: Entität und Periode

**Grundregeln**

- **Monatlich (`MONTH`):** alles, was mit Betreuung und Geld pro Monat zu tun hat, und Zustände, die sich unterjährig ändern können (Pensum, Wohnsitz, Einrichtung). Der Beitrag wird pro Monat berechnet.
- **Jährlich (`YEAR`):** nur das Einkommen, weil es auf der Steuerveranlagung beruht (KiBG 5.3). Monatliche Formeln lesen es für das laufende Jahr.
- **Unbefristet (`ETERNITY`):** Daten, die sich nie ändern (Geburtsdatum, Betreuungsbeginn, Gesuchsdatum).

**Entscheide für die ersten Tests**

- **Massgebendes Einkommen ist eine Eingabe.** Wir geben das massgebende Einkommen pro Person direkt ein (`me_steuerveranlagung`) und berechnen es nicht nach der V EG-KVG (O5). OpenFisca zählt nur zusammen, wessen Einkommen gemäss KiBV 8 dazugehört.
- **Betreuungsstunden pro Monat sind eine Eingabe.** Wir geben die Stunden pro Monat direkt ein (`betreuungsstunden`), nicht Tage und Wochen. Die Obergrenze von 12 Stunden pro Tag prüfen wir über die Anzahl Betreuungstage: höchstens Tage × 12. Für die Obergrenze von 5 Tagen pro Woche fehlt die Umrechnung auf einen Monat (O7). Bis das geklärt ist, kürzt OpenFisca bei dieser Grenze nichts: Wir nehmen an, dass die eingegebenen Tage und Stunden höchstens 5 Tage pro Woche umfassen. Gibt jemand Samstagsbetreuung ein, rechnet der Rechner einen zu hohen Beitrag aus. Das ist selten, weil die meisten Kitas nur Montag bis Freitag geöffnet sind.

| Variable | Entität | Periode | Eingabe / Formel | Typ | Quelle |
|---|---|---|---|---|---|
| `geburtsdatum` | Person | ETERNITY | Eingabe, **Pflicht für jedes Kind** (fehlt es, bricht die Berechnung mit einer Fehlermeldung ab) | Datum | KiBG 4.3, KiBV 14 |
| `kibg_alter_monate` | Person (Kind) | MONTH | Formel | volle Monate am Monatsersten (A1) | KiBG 4.3, KiBV 14 |
| `wohnsitz_kanton_sg` | Person | MONTH | Eingabe | ja/nein | KiBG 4.1 |
| `kibg_gesuchstellend` | Person | MONTH | Eingabe, **Pflicht bei zwei Erziehungsberechtigten im Haushalt** | ja/nein | KiBG 9.1, KiBV 8.1b |
| `kibg_gesuchsteller` | Person | MONTH | Formel (angegebene Person oder einzige erziehungsberechtigte Person; sonst Fehlermeldung) | ja/nein | KiBG 9.1, KiBV 8.1b |
| `beschaeftigungsgrad` | Person | MONTH | Eingabe | Anteil (0.8 = 80 %) | KiBG 4.1 |
| `me_steuerveranlagung` | Person | YEAR | Eingabe | Fr. | KiBG 5.3, KiBV 9 |
| `me_aktuell` | Person | YEAR | Eingabe | Fr. (aufs Jahr gerechnet) | KiBG 5.4, KiBV 11 |
| `besteuerungsart` | Person | YEAR | Eingabe | Kategorie | KiBV 10.1 |
| `kibg_einrichtungstyp` | Person (Kind) | MONTH | Eingabe | Kategorie | KiBG 3.2 |
| `kibg_einrichtung_anerkannt` | Person (Kind) | MONTH | Eingabe | ja/nein | KiBG 3.2 |
| `kibg_einrichtung_angemeldet` | Person (Kind) | MONTH | Eingabe | ja/nein | KiBG 3.3 |
| `kibg_einrichtung_berechtigt` | Person (Kind) | MONTH | Formel | ja/nein | KiBG 3.1 |
| `eingeschult` | Person (Kind) | MONTH | Eingabe (ab Eintritt in den obligatorischen Kindergarten, A8) | ja/nein | KiBV 14.2–3, 16.1 |
| `primarschule_abgeschlossen` | Person (Kind) | MONTH | Eingabe | ja/nein | KiBG 4.3 |
| `kibg_alter_erfuellt` | Person (Kind) | MONTH | Formel | ja/nein | KiBG 4.3 |
| `kibg_altersstufe` | Person (Kind) | MONTH | Formel | Kategorie | KiBV 14.1–3 |
| `kibg_hoechstbeitrag` | Person (Kind) | MONTH | Formel | Fr. pro Stunde | KiBV 14 |
| `betreuungsstunden` | Person (Kind) | MONTH | Eingabe | Stunden | KiBV 14.4 |
| `betreuungstage_mit_obhut` | Person (Kind) | MONTH | Eingabe | Tage | KiBV 7, 14.4 |
| `kibg_subventionierte_stunden` | Person (Kind) | MONTH | Formel | Stunden | KiBV 14.4 |
| `kibg_betreuungskosten` | Person (Kind) | MONTH | Eingabe | Fr. | KiBG 6.2 |
| `kibg_anspruch` | Person (Kind) | MONTH | Formel | ja/nein | KiBG 4 |
| `kibg_beitrag_pro_stunde` | Person (Kind) | MONTH | Formel (Formel im Anhang) | Fr. pro Stunde | KiBV 13, Anhang |
| `kibg_mindestbeitrag_pro_stunde` | Person (Kind) | MONTH | Formel (Formel im Anhang ohne Z1, Z2) | Fr. pro Stunde | KiBG 6.1, 20.1; KiBV 13, Anhang |
| `kibg_zusatzbeitrag_pro_stunde` | Person (Kind) | MONTH | Formel (B − Mindestbeitrag pro Stunde) | Fr. pro Stunde | KiBG 20.2, KiBV 24 |
| `kibg_mindestbeitrag` | Person (Kind) | MONTH | Formel | Fr. | KiBG 6.1–2, 20.1; KiBV 14.4 |
| `kibg_zusatzbeitrag` | Person (Kind) | MONTH | Formel | Fr. | KiBG 20.2, KiBV 24 |
| `kibg_beitrag_total` | Person (Kind) | MONTH | Formel | Fr. | KiBG 20.3 |
| `kibg_restkosten_eltern` | Person (Kind) | MONTH | Formel | Fr. | KiBG 12.2 |
| `kibg_anteil_kanton` | Person (Kind) | MONTH | Formel | Fr. | KiBG 18.1 |
| `kibg_anteil_gemeinde` | Person (Kind) | MONTH | Formel | Fr. | KiBG 18.1, 20.2 |
| `betreuungsbeginn` | Person (Kind) | ETERNITY | Eingabe | Datum | KiBG 9.2 |
| `kibg_gesuchsdatum` | Person (Kind) | ETERNITY | Eingabe | Datum | KiBG 9.1 |
| `kibg_beitragsbeginn` | Person (Kind) | ETERNITY | Formel (optional) | Datum | KiBG 9.2, KiBV 25 |
| `kibg_verfuegung_ende` | Person (Kind) | ETERNITY | Formel (optional) | Datum | KiBV 16 |
| `gemeinsamer_haushalt` | Haushalt | MONTH | Eingabe | ja/nein | KiBG 4.1b |
| `kibg_beschaeftigung_lit_a_erfuellt` | Haushalt | MONTH | Formel | ja/nein | KiBG 4.1a |
| `kibg_beschaeftigung_lit_b_erfuellt` | Haushalt | MONTH | Formel (nur bei gemeinsamem Haushalt anwendbar) | ja/nein | KiBG 4.1b |
| `kibg_beschaeftigung_erfuellt` | Haushalt | MONTH | Formel (lit. a UND lit. b, O3) | ja/nein | KiBG 4.1 |
| `kibg_wohnsitz_erfuellt` | Haushalt | MONTH | Formel | ja/nein | KiBG 4.1; erfüllt, wenn die gesuchstellende Person im Kanton wohnt (O8) |
| `kibg_ausnahme_bewilligt` | Haushalt | MONTH | Eingabe | ja/nein | KiBG 4.2 |
| `kibg_ausnahmegrund` | Haushalt | MONTH | Eingabe | Kategorie | KiBV 12 |
| `verheiratet_oder_eingetragen` | Haushalt | MONTH | Eingabe | ja/nein | KiBV 8.2a |
| `beginn_gemeinsamer_haushalt` | Haushalt | ETERNITY | Eingabe | Datum | KiBV 8.2b |
| `kibg_gefestigte_lebensgemeinschaft` | Haushalt | MONTH | Formel | ja/nein | KiBV 8.2 |
| `kibg_antrag_aktuelle_gegebenheiten` | Haushalt | YEAR | Eingabe | ja/nein | KiBV 11.1 |
| `kibg_massgebendes_einkommen` | Haushalt | MONTH | Formel (Summe der Eingaben) | Fr. | KiBG 5, KiBV 8–11. Monatlich, weil sich der Haushalt (Partner/in) im Jahr ändern kann; die Einkommen selbst sind Jahreswerte |
| `kibg_einkommensfaktor` | Haushalt | MONTH | Formel | Anteil 0–1 | KiBV 15, Anhang |
| `wohngemeinde` | Haushalt | MONTH | Eingabe | Kategorie | KiBV 2 |
| `kibg_zusatzbeitrag_z1` | Haushalt | MONTH | Eingabe | Fr. pro Stunde | KiBG 20.2, KiBV 24 |
| `kibg_zusatzbeitrag_z2` | Haushalt | MONTH | Eingabe | Fr. pro Stunde | KiBG 20.2, KiBV 24 |

---

## KiBG (Gesetz)

### I. Allgemeine Bestimmungen

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 1 | Zweck: Vereinbarkeit von Familie und Erwerbstätigkeit | Nicht berechenbar | — | Gehört in die Dokumentation |
| Art. 2.1 | Begriff Erziehungsberechtigte | Entität | Rolle `erziehungsberechtigt` | Die Obhut wird über die Rolle angenommen |
| Art. 2.2 | Begriff Tagesfamilienorganisation | Variable (Kategorienwert) | `tagesfamilie` in `kibg_einrichtungstyp` | — |

### II. Anspruch und Bemessung

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 3.1 | Nur für anerkannte **und** angemeldete Einrichtungen | Variable, Formel | `kibg_einrichtung_berechtigt` (Kind) | = anerkannt UND angemeldet |
| Art. 3.2 a–d | Anerkannte Einrichtungstypen | Variable, Eingabe (Kategorie) | `kibg_einrichtungstyp`: `kita` / `tagesfamilie` / `schulergaenzend` / `sonderschule` / `keine` | Der Höchstbeitrag richtet sich nach der Betreuungsform (KiBV 14.3), nicht nach der Schule |
| Art. 3.2 (Kriterien) | Bewilligung, Qualitätskonzept, Leistungsvereinbarung | Variable, Eingabe (ja/nein) | `kibg_einrichtung_anerkannt` | Behördlicher Entscheid, daher Eingabe |
| Art. 3.3 | Bei der kantonalen Stelle angemeldet | Variable, Eingabe (ja/nein) | `kibg_einrichtung_angemeldet` | Beginn gemäss KiBV 6 |
| Art. 4.1 | Zivilrechtlicher Wohnsitz im Kanton | Variable, Eingabe (ja/nein) + Formel | `wohnsitz_kanton_sg` (Person), `kibg_gesuchsteller` (Person), `kibg_wohnsitz_erfuellt` (Haushalt) | Nur die gesuchstellende Person muss hier wohnen (O8, entschieden) |
| Art. 4.1 | Selbständig oder unselbständig erwerbstätig, mit Beschäftigungsgrad | Variable, Eingabe (Anteil) | `beschaeftigungsgrad` (Person) | Als Anteil: 80 % = 0.8 |
| Art. 4.1a | Mindestens 20 Prozent | Parameter | `kibg.anspruch.min_beschaeftigungsgrad = 0.20` | Einheit `/1` (OpenFisca-Konvention) |
| Art. 4.1b | Zusammen mindestens 120 Prozent bei gemeinsamem Haushalt | Parameter + Eingabe | `kibg.anspruch.min_beschaeftigungsgrad_gemeinsam = 1.20`, `gemeinsamer_haushalt` (Haushalt) | Kumulativ zu lit. a: jeder Elternteil mindestens 20 % (O3, entschieden) |
| Art. 4.1 | Beschäftigungsbedingung erfüllt | Variable, Formel | `kibg_beschaeftigung_lit_a_erfuellt`, `kibg_beschaeftigung_lit_b_erfuellt`, `kibg_beschaeftigung_erfuellt` (Haushalt) | Jeder Erziehungsberechtigte mindestens 20 % (a); im gemeinsamen Haushalt zusätzlich zusammen mindestens 120 % (b) (O3) |
| Art. 4.2 | Ausnahme in begründeten Fällen | Variable, Eingabe (ja/nein) | `kibg_ausnahme_bewilligt` | Menschlicher Entscheid; Gründe in KiBV 12 |
| Art. 4.3 | Ab drei Monaten | Parameter + Eingabe | `kibg.anspruch.mindestalter_monate = 3`, `geburtsdatum` | — |
| Art. 4.3 | Bis zum Abschluss der Primarschule | Variable, Eingabe (ja/nein) | `primarschule_abgeschlossen` (Kind) | Eine Tatsache, kein Alter |
| Art. 4.3 | Altersbedingung erfüllt | Variable, Formel | `kibg_alter_erfuellt` (Kind) | mindestens 3 Monate UND Primarschule nicht abgeschlossen |
| Art. 4 | Anspruch gesamt | Variable, Formel | `kibg_anspruch` (Kind) | `kibg_wohnsitz_erfuellt` UND (`kibg_beschaeftigung_erfuellt` ODER `kibg_ausnahme_bewilligt`) UND `kibg_alter_erfuellt` UND `kibg_einrichtung_berechtigt` |
| Art. 5.1–5.2 | Abhängig von massgebendem Einkommen und Vermögen (ME) | Variable | `kibg_massgebendes_einkommen` (Haushalt, jährlich) | Zusammengesetzt gemäss KiBV 8–11 |
| Art. 5.3 | Grundlage: letzte definitive Steuerveranlagung | Variable, Eingabe | `me_steuerveranlagung` (Person, jährlich) | In einem anderen Erlass definiert, der V EG-KVG (O5). **Entscheid: direkte Eingabe** |
| Art. 5.4 | Wesentliche Veränderung, daher aktuelle Gegebenheiten | Variable, Eingabe + Formel | `me_aktuell` (Person) | Schwelle in KiBV 11 |
| Art. 6.1 | Lineares Modell | Variable, Formel | `kibg_mindestbeitrag_pro_stunde` | Formel im Anhang der KiBV ohne Zusatzbeiträge |
| Art. 6.2 | Beitrag höchstens so hoch wie die tatsächlichen Kosten | Variable, Eingabe + Formel | `kibg_betreuungskosten` (Kind, monatlich), `kibg_mindestbeitrag` | min(Beitrag, Kosten) |

### III. Plattform

| Ref. | Inhalt | Konzept | Bemerkung |
|---|---|---|---|
| Art. 7 | Gemeinsame elektronische Plattform | Nicht berechenbar | — |
| Art. 8.1–8.2 | Datenbearbeitung, auch besonders schützenswerter Daten | Nicht berechenbar | Wichtig für den Teil zu Ethik und Datenschutz |

### IV. Verfahren

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 9.1 | Beiträge nur auf Gesuch der Erziehungsberechtigten | Variable, Eingabe (Datum, ja/nein) | `kibg_gesuchsdatum`, `kibg_gesuchstellend` | Wer das Gesuch stellt, bestimmt den massgebenden Wohnsitz (O8) |
| Art. 9.2 | Rückwirkend, wenn das Gesuch innert 30 Tagen nach Betreuungsbeginn eingeht, sonst ab Gesuch | Parameter + Eingabe + Formel | `kibg.verfahren.frist_rueckwirkung_tage = 30`, `betreuungsbeginn`, `kibg_beitragsbeginn` | Übergangsfrist in KiBV 25 |
| Art. 10 | Einrichtung bestätigt das Betreuungsverhältnis | Variable, Eingabe (ja/nein) (optional) | `betreuung_bestaetigt` | Kann weggelassen werden |
| Art. 11.1 | Kommunale Stelle prüft und verfügt | Nicht berechenbar | — | **Unser Ergebnis ist eine Schätzung, keine Verfügung** |
| Art. 11.2 | In der Regel zwölf Monate | Parameter | `kibg.verfahren.verfuegungsdauer_monate = 12` | Einzelheiten in KiBV 16 |
| Art. 11.3 | Verfügung wird bei Änderungen angepasst | Nicht berechenbar | — | — |
| Art. 12.1, 12.3 | Auszahlung an die Einrichtung; Kantonsanteil an die Gemeinde | Nicht berechenbar | — | — |
| Art. 12.2 | Beitrag wird auf der Rechnung an die Eltern abgezogen | Variable, Formel | `kibg_restkosten_eltern` | = Kosten − Beitrag. Gut für den Rechner |
| Art. 13 | Unrechtmässig bezogene Beiträge: Rückforderung oder Verrechnung innert fünf Jahren seit Rechtskraft der Verfügung | **Zurückgestellt (R1)** | — | Siehe R1 |
| Art. 14–15 | Mitwirkungspflichten von Eltern und Einrichtungen | Nicht berechenbar | — | — |
| Art. 16.1 | Controlling und Stichproben | Nicht berechenbar | — | — |
| Art. 16.2 | Modell wird regelmässig überprüft | Nicht berechenbar | — | Stützt die Reformidee |

### V. Finanzierung

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 17.1 | 20 Mio. Franken pro Jahr | Parameter | `kibg.finanzierung.gesamtvolumen = 20_000_000` | Nur für Simulationen |
| Art. 17.2 | ± Fr. 500'000 in drei aufeinanderfolgenden Jahren führt zur Anpassung | Parameter | `toleranz = 500_000`, `jahre = 3` | Braucht Bevölkerungsdaten, daher nur als Reformszenario |
| Art. 18.1 | Kanton und Gemeinde tragen je die Hälfte | Parameter + Formel | `kibg.finanzierung.anteil_kanton = 0.5`, `kibg_anteil_kanton`, `kibg_anteil_gemeinde` | Gilt nur für den Mindestbeitrag |
| Art. 18.2 | Gebundene Ausgabe | Nicht berechenbar | — | — |
| Art. 19 | Vollzugskosten nicht aus dem Budget | Nicht berechenbar | — | — |

### VI. Weitere kommunale Finanzierung

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 20.1 | Beiträge nach Art. 6/17/18 sind Mindestbeiträge | Variable, Formel | `kibg_mindestbeitrag_pro_stunde`, `kibg_mindestbeitrag` | — |
| Art. 20.2 | Gemeinde kann mit Zusatzbeiträgen aufstocken | Variable, Eingabe | `kibg_zusatzbeitrag_z1`, `kibg_zusatzbeitrag_z2` (Haushalt, Fr./Stunde) | Werte pro Gemeinde unbekannt, daher Eingaben |
| Art. 20.3 | Mindestbeitrag + Zusatzbeitrag höchstens so hoch wie die Kosten | Variable, Formel | `kibg_beitrag_total` | min(Mindest- + Zusatzbeitrag, Kosten) |
| Art. 21 | Anderweitige kommunale Unterstützung | Ausserhalb des Umfangs | — | — |

### VII–VIII. Vollzug und Schlussbestimmungen

| Ref. | Inhalt | Konzept | Bemerkung |
|---|---|---|---|
| Art. 22 | Zuständigkeiten | Nicht berechenbar | — |
| Art. 23 | Delegation an die Verordnung | Nicht berechenbar | Verweist auf die KiBV |
| III. | Aufhebung des Gesetzes vom 29. November 2020 | Periode | Das alte Gesetz fehlt in den Unterlagen, daher keine Historie vor Vollzugsbeginn |
| IV.1 | Regierung bestimmt den Vollzugsbeginn | Periode | O1 |

---

## KiBV (Verordnung, Entwurf)

### I. Allgemeine Bestimmungen

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 1 | Zuständige Stelle: Amt für Soziales | Nicht berechenbar | — | — |
| Art. 2 | Zuständige Gemeinde: Wohnsitz der anspruchsberechtigten Eltern | Variable, Eingabe | `wohngemeinde` (Haushalt) | Bestimmt Z1/Z2. Bei getrennten Eltern: Gemeinde der gesuchstellenden Person (O8, entschieden) |

### II. Anmeldung von Einrichtungen

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 3–5 | Anmeldung, Inhalt, Prüfung | Nicht berechenbar | — | Vereinfacht zu `kibg_einrichtung_angemeldet` |
| Art. 6 | Teilnahme beginnt am Ersten des Folgemonats nach der Bestätigung | Variable, Formel (optional) | `kibg_einrichtung_teilnahmebeginn` | Kann weggelassen werden |

### III. Anspruch und Bemessung

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 7 | Nur für Tage mit faktischer Obhut **und** genutzter Betreuung | Variable, Eingabe | `betreuungstage_mit_obhut` (Kind, monatlich) | Bei alternierender Obhut gibt jeder Elternteil nur seine eigenen Tage ein (O10) |
| Art. 8.1a | Gemeinsamer Haushalt: Einkommen beider Eltern | Variable, Formel | Teil von `kibg_massgebendes_einkommen` | Summe über Rolle `erziehungsberechtigt` |
| Art. 8.1b | Getrennter Haushalt: Gesuchsteller/in + gefestigte Partnerin oder gefestigter Partner, die oder der nicht erziehungsberechtigt ist | Variable, Formel | Teil von `kibg_massgebendes_einkommen` | Braucht Rolle `partner` |
| Art. 8.2a | Gefestigt = Ehe oder eingetragene Partnerschaft | Variable, Eingabe | `verheiratet_oder_eingetragen` | — |
| Art. 8.2b | Gefestigt = seit mindestens zwei Jahren gemeinsamer Haushalt (Konkubinat) | Parameter + Eingabe | `kibg.einkommen.mindestdauer_konkubinat_jahre = 2`, `beginn_gemeinsamer_haushalt` | — |
| Art. 8.2 | Gefestigte Lebensgemeinschaft | Variable, Formel | `kibg_gefestigte_lebensgemeinschaft` | a ODER b |
| Art. 9 | Ordentlich Besteuerte: ME nach Art. 12 Abs. 2 V EG-KVG | Variable, Eingabe | `me_steuerveranlagung` | Externer Erlass (O5) |
| Art. 10.1 | Quellenbesteuerte oder ohne Veranlagung: nach Art. 12bis V EG-KVG | Variable, Eingabe (Kategorie) | `besteuerungsart` | Externer Erlass (O5) |
| Art. 10.2 | Einkommens- und Vermögensnachweise einreichen | Nicht berechenbar | — | — |
| Art. 11.1 | Aktuelle Gegebenheiten nur auf Antrag | Variable, Eingabe (ja/nein) | `kibg_antrag_aktuelle_gegebenheiten` | — |
| Art. 11.2 | Abweichung von mindestens 25 % bei Gesuchstellung | Parameter + Formel | `kibg.einkommen.schwelle_abweichung = 0.25`, `kibg_massgebendes_einkommen` | In beide Richtungen (O12, entschieden) |
| Art. 11.3 | Veränderung von mindestens 25 % während laufender Verfügung gilt ab dem Ersten des Folgemonats | Formel (optional) | — | Datumslogik, kann weggelassen werden |
| Art. 12 a–c | Ausnahmegründe: berufliche Integration, familiäre Belastung, Indikation beim Kind | Variable, Eingabe (Kategorie) | `kibg_ausnahmegrund` (Bezeichnungen im Wortlaut von lit. a–c) | Dokumentiert den Grund; der Entscheid bleibt bei `kibg_ausnahme_bewilligt` |

### IV. Berechnung

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 13 | Formel im Anhang | Variable, Formel | `kibg_beitrag_pro_stunde` | — |
| Art. 14.1a | Unter 18 Monaten, Kita: Fr. 11.00 | Parameter | `kibg.hoechstbeitrag.unter_18_monate.kita = 11.00` | Gilt die vollen ersten 18 Lebensmonate (O2, entschieden) |
| Art. 14.1b | Unter 18 Monaten, Tagesfamilie: Fr. 8.30 | Parameter | `…unter_18_monate.tagesfamilie = 8.30` | — |
| Art. 14.2a | Über 18 Monaten bis Einschulung, Kita: Fr. 7.50 | Parameter | `…ueber_18_monate.kita = 7.50` | Ab dem 18-Monate-Geburtstag (O2) |
| Art. 14.2b | Über 18 Monaten bis Einschulung, Tagesfamilie: Fr. 5.50 | Parameter | `…ueber_18_monate.tagesfamilie = 5.50` | — |
| Art. 14.3a | Eingeschult bis Ende Primarstufe, Kita: Fr. 7.50 | Parameter | `…eingeschult.kita = 7.50` | — |
| Art. 14.3b | Eingeschult, schulergänzende Betreuung: Fr. 5.50 | Parameter | `…eingeschult.schulergaenzend = 5.50` | — |
| Art. 14.3c | Eingeschult, Tagesfamilie: Fr. 5.50 | Parameter | `…eingeschult.tagesfamilie = 5.50` | — |
| Art. 14.1–3 | Welche Altersstufe gilt | Variable, Eingabe + Formel | `eingeschult` (ja/nein), `kibg_altersstufe` | Die Einschulung ist eine Tatsache, kein Alter |
| Art. 14.1–3 | Massgebender Höchstbeitrag | Variable, Formel | `kibg_hoechstbeitrag` (Kind) | Altersstufe × Einrichtungstyp |
| Art. 14.4 | Höchstens 12 subventionierte Stunden pro Tag | Parameter | `kibg.betreuung.max_stunden_pro_tag = 12` | — |
| Art. 14.4 | Höchstens 5 Tage pro Woche | Parameter | `kibg.betreuung.max_tage_pro_woche = 5` | — |
| Art. 14.4 | Subventionierte Stunden | Variable, Eingabe + Formel | `betreuungsstunden` (Kind, monatlich), `kibg_subventionierte_stunden` | **Entscheid: Stunden pro Monat als Eingabe**; min(Stunden, Betreuungstage × 12). Tagesgrenze pro Woche offen (O7) |
| Art. 14.5 | Betreuungsmodule und Monatspauschalen per Richtlinien | Ausserhalb des Umfangs | — | Die Richtlinien liegen nicht vor (O7) |
| Art. 15.1 | Kleinstes ME Fr. 40'000; bis dahin voller Beitrag | Parameter + Formel | `kibg.einkommen.min = 40_000` | Faktor nach oben begrenzt |
| Art. 15.2 | Höchstes ME Fr. 154'000; darüber kein Beitrag | Parameter + Formel | `kibg.einkommen.max = 154_000` | Gilt nur für den Mindestbeitrag; Z2 wird auch darüber ausgerichtet (O4, entschieden) |

### V. Verfahren für die Ausrichtung der Beiträge

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 16.1 | Kita und Tagesfamilie: 12 Monate, im Jahr der Einschulung bis Schuljahresbeginn | Formel (optional) | `kibg_verfuegung_ende` | — |
| Art. 16.2 | Eingeschulte Kinder: ein Schuljahr, oder bis zum Ende des laufenden | Formel (optional) | `kibg_verfuegung_ende` | Schuljahresbeginn vorläufig 1. August (O9) |
| Art. 16.3 | Senkungen wegen Modelländerungen gelten erst ab der nächsten Verfügung | Periode | — | Wichtig für Reformszenarien |
| Art. 16.4 | Erinnerung vor Ablauf einer Verfügung | Nicht berechenbar | — | — |
| Art. 17 | Erfassung des Betreuungsumfangs bis zum 15., Auszahlungsrhythmus | Nicht berechenbar | — | — |
| Art. 18 | Unrecht bezogen, wenn die Anspruchsvoraussetzungen nicht erfüllt waren; Forderung richtet sich gegen die Eltern | **Zurückgestellt (R1)** | — | Konkretisiert KiBG 13, siehe R1 |

### VI. Plattform

| Ref. | Inhalt | Konzept | Bemerkung |
|---|---|---|---|
| Art. 19–20 | Betrieb, Login | Nicht berechenbar | — |
| Art. 21 | Datenkategorien (u. a. AHV-Nummer, Steuerdaten, Sozialhilfe) | Nicht berechenbar | **Ethik:** Unser Rechner braucht viel weniger, das ist Datenminimierung |
| Art. 22 | Zugriffsrechte | Nicht berechenbar | — |
| Art. 23 | Protokollierung, 10 Jahre Aufbewahrung | Nicht berechenbar | Unser Rechner speichert nichts |

### VII. Weitere kommunale Finanzierung

| Ref. | Inhalt | Konzept | Bemerkung |
|---|---|---|---|
| Art. 24 | Zusatzbeiträge einkommensabhängig (Z1) oder einkommensunabhängig (Z2) | Variable | Bestätigt die Bedeutung von Z1 und Z2 in der Formel |

### VIII. Schlussbestimmungen

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 25.1 | Gesuche innert drei Monaten nach Vollzugsbeginn gelten rückwirkend ab Vollzugsbeginn | Parameter + Formel | `kibg.uebergang.frist_monate = 3` | Ersetzt in der Übergangszeit die 30 Tage aus KiBG 9.2 |
| Art. 25.2 | KiBV 16 gilt sachgemäss | — | — | — |
| II. | Änderung der Delegationsverordnung | Nicht berechenbar | — | — |
| IV. | Anwendung «ab ●●» | Periode | — | O1 |

### Anhang: die Formel

**B = (MaxV + Z1) × (1 − (ME − MinmE) / (MaxmE − MinmE)) + Z2**

| Formelteil | Konzept | Quelle |
|---|---|---|
| B: Beitrag je Kind und Betreuungsstunde | Variable, Formel `kibg_beitrag_pro_stunde` | Anhang |
| MaxV | Variable, Formel `kibg_hoechstbeitrag` | KiBV 14 |
| MinmE, MaxmE | Parameter | KiBV 15 |
| ME | Variable `kibg_massgebendes_einkommen` | KiBV 8–11 |
| Z1, Z2 | Variablen, Eingaben | KiBG 20, KiBV 24 |
| Faktor 1 − (ME − MinmE) / (MaxmE − MinmE), begrenzt auf 0–1 | Variable, Formel `kibg_einkommensfaktor` | Anhang; Begrenzung aus KiBV 15, die Formel selbst begrenzt nicht |

**Hinweis zur Modellierung:** Die Formel steht im Text einmal (Anhang, Verweis in KiBV 13) und deshalb im Code nur einmal (`formel_anhang`). Sie wird dort angewendet, wo der Text sie anwendet: für B mit Z1 und Z2 (`kibg_beitrag_pro_stunde`) und für den Mindestbeitrag nach KiBG 6 und 20.1 ohne Zusatzbeiträge (`kibg_mindestbeitrag_pro_stunde`). Der Zusatzbeitrag ist, was die Gemeinde nach KiBG 20.2 «über ihren Kostenanteil hinaus» aufstockt: B minus Mindestbeitrag (`kibg_zusatzbeitrag_pro_stunde`). Den Mindestbeitrag tragen Kanton und Gemeinde je hälftig (KiBG 18), den Zusatzbeitrag die Gemeinde allein (KiBG 20.2).

**Berechnungskette:**

1. Anspruch
2. massgebendes Einkommen (ME)
3. Höchstbeitrag
4. Beitrag pro Stunde
5. × subventionierte Stunden
6. auf die Kosten begrenzt
7. aufgeteilt auf Kanton, Gemeinde und Restkosten der Eltern
8. Monatsbeträge kaufmännisch auf 5 Rappen gerundet. **Teamentscheid, steht nicht im Text**; Regeln in `szenarien.md`, Annahme A4

---

## Zurückgestellt, aber relevant

Diese Bestimmungen modellieren wir anfangs bewusst nicht. Sie sind aber wichtig für die Dokumentation, den Pitch oder einen späteren Ausbau.

| Nr. | Bestimmung | Inhalt | Warum relevant | Warum zurückgestellt | Mögliche Umsetzung später |
|---|---|---|---|---|---|
| R1 | KiBG 13, KiBV 18 | Unrechtmässig bezogene Beiträge werden innert fünf Jahren seit Rechtskraft der Verfügung zurückgefordert oder mit weiteren Beiträgen verrechnet. Unrecht bezogen ist, was ohne erfüllte Anspruchsvoraussetzungen bezogen wurde. Die Forderung richtet sich gegen die Eltern. | Zeigt das Risiko für Familien, wenn sich Einkommen, Pensum oder Betreuung ändern und das nicht gemeldet wird (Mitwirkungspflicht KiBG 14.2, Anpassung KiBG 11.3). Unser Rechner sollte darauf hinweisen. Gut für den Teil zu Ethik und Nutzerinformation. | Betrifft nicht die Berechnung des Beitrags, sondern ein späteres Verfahren. Ob ein Bezug unrechtmässig war, entscheidet die kommunale Stelle. | Parameter `kibg.verfahren.rueckforderungsfrist_jahre = 5`; Eingaben `kibg_bezogener_beitrag`, `rechtskraft_verfuegung`; Formeln `kibg_rueckforderungsbetrag` = bezogen − Anspruch nach den tatsächlichen Verhältnissen, `kibg_rueckforderung_moeglich` (Frist noch offen) |

---

## Offene Fragen (für das Rechtsteam und zugleich für die Stellungnahme zur Verordnung)

| Nr. | Frage | Quelle |
|---|---|---|
| O1 | Kein Vollzugsbeginn («ab ●●»). **Entschieden:** Platzhalter 2028-08-01 (`formula_2028_08`), ersetzen sobald der Vollzugsbeginn feststeht | KiBG IV.1, KiBV IV |
| O2 | Ein Kind mit genau 18 Monaten fällt zwischen «unter 18» und «über 18». **Entschieden:** Der höhere Ansatz gilt die vollen ersten 18 Lebensmonate; ab dem 18-Monate-Geburtstag (erster Tag des 19. Lebensmonats) gilt der tiefere. Mit dem Stichtag Monatserster: Wer am Ersten des Monats mindestens 18 Monate alt ist, erhält in diesem Monat den tieferen Ansatz | KiBV 14.1–14.2 |
| O3 | Braucht es bei 120 % zusammen zusätzlich mindestens 20 % pro Elternteil? Und gilt «a» nur für Alleinerziehende? **Entschieden: lit. a und b kumulativ.** Jeder Elternteil muss mindestens 20 % und beide zusammen mindestens 120 % arbeiten; 120 % / 0 % gibt keinen Anspruch (ausser mit Ausnahme nach Abs. 2). Begründung: Wortlaut (die Erziehungsberechtigten müssen «eine Erwerbstätigkeit ausüben», je einzeln; über 100 % für eine Person ist atypisch), Systematik (120 = 100 + 20 baut auf lit. a auf; Abs. 2 löst atypische Fälle), Rechtsgleichheit (Art. 8 BV: Paare nicht tiefer als Alleinerziehende), Zweck (ohne Erwerbstätigkeit eines Elternteils fehlt der Betreuungsbedarf) | KiBG 4.1 |
| O4 | Gilt Z2 (einkommensunabhängig) auch über Fr. 154'000? **Entschieden: ja.** Z2 ist per Definition einkommensunabhängig (KiBV 24); KiBV 15.2 betrifft den Mindestbeitrag | KiBV 15.2 vs. Anhang |
| O5 | Das massgebende Einkommen ist in einem anderen Erlass definiert (V EG-KVG, sGS 331.111), der in den Unterlagen fehlt. **Vorläufig entschieden:** Einkommen pro Person ist eine Eingabe | KiBV 9–10 |
| O6 | Das Gesetzes-PDF ist die **Fassung der ersten Lesung (16. September 2025)**, die KiBV verweist aber auf das Gesetz vom 14. Juni 2026. Bei den Organisatoren nachfragen, ob der Schlusstext abweicht | KiBG Titelseite |
| O7 | Umrechnung der Wochenobergrenzen auf einen Monat; Betreuungsmodule und Monatspauschalen sind Richtlinien überlassen, die nicht öffentlich sind. **Vorläufig entschieden:** Stunden pro Monat sind eine Eingabe; die Grenze von 5 Tagen pro Woche bleibt offen | KiBV 14.4–14.5 |
| O8 | Welcher Elternteil muss im Kanton wohnen, und welche Gemeinde ist zuständig, wenn die Eltern getrennt leben? **Entschieden:** Die gesuchstellende Person muss im Kanton wohnen; zuständig ist ihre Wohngemeinde | KiBG 4.1, KiBV 2 |
| O9 | Das Datum des Schuljahresbeginns steht nicht im Text. **Vorläufig:** 1. August; nur für die optionalen Datumsregeln nötig | KiBV 16.2 |
| O10 | Getrennte Eltern mit alternierender Obhut: Wer stellt das Gesuch, und wie werden die Tage aufgeteilt? **Entschieden:** Jeder Elternteil stellt das Gesuch für die eigenen Obhutstage und gibt nur diese ein | KiBV 7, 8.1b |
| O11 | ~~Private Sonderschulen (KiBG 3.2d): welcher Ansatz?~~ **Erledigt:** Der Anspruch folgt aus KiBG 3.2d; der Betrag richtet sich nach der Betreuungsform (KiBV 14.3) | KiBG 3.2d, KiBV 14.3 |
| O12 | Zählt die Abweichung von 25 % in beide Richtungen (nach oben und unten)? **Entschieden: ja**, wie im Wortlaut («Abweichung») | KiBV 11.2–11.3 |

---

## Vorgeschlagene Reihenfolge für das Programmieren

1. Zuerst der Kern: Anspruch (KiBG 3–4), massgebendes Einkommen (KiBV 8 und 11), die Formel mit Ansätzen und Grenzen (KiBV 13–15, Anhang), die Stundenobergrenzen und die Kostenobergrenze.
2. Danach die Aufteilung der Finanzierung und die Restkosten.
3. Optional: die Datumsregeln (KiBG 9.2, KiBV 16, 25) und die Budgetsimulation (KiBG 17).
