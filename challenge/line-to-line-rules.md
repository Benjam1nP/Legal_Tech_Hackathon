# Regelinventar KiBG / KiBV (Zeile für Zeile)

Jede Bestimmung des Gesetzes (KiBG, `Gesetz.pdf`) und der Verordnung (KiBV, `Verordnung.pdf`, Entwurf) ist hier einem der vier OpenFisca-Konzepte zugeordnet: **Periode**, **Parameter**, **Entität**, **Variable**.

**Legende**

- **Nicht berechenbar:** Verfahren, Datenschutz, Finanzverwaltung. Gehört in die Dokumentation, nicht in den Code.
- **Ausserhalb des Umfangs:** grundsätzlich berechenbar, aber nicht Teil der Berechnung für eine Familie.
- **Zurückgestellt (R1, R2 …):** relevant, wird aber anfangs bewusst nicht modelliert. Details im Abschnitt «Zurückgestellt, aber relevant».
- Variablen sind entweder **Eingaben** (Tatsachen oder menschliche Entscheide, welche die Nutzerin oder der Nutzer eingibt) oder **Formeln** (von OpenFisca berechnet).
- Die Namen sind Vorschläge und können geändert werden.
- **O1, O2 …** verweisen auf die offenen Fragen am Schluss.
- **Periode:** Alle Parameter gelten ab Vollzugsbeginn, der noch nicht feststeht (O1). Die meisten Variablen sind monatlich, das Einkommen jährlich, Daten sind taggenau.

---

## Entitäten (Struktur)

| Entität / Rolle | Quelle | Bemerkung |
|---|---|---|
| `Person` | — | Einzelpersonen: Eltern, Partner/in, Kind |
| `Household`, Rolle `erziehungsberechtigt` (max. 2) | KiBG 2.1 | Personen, die das Kind in Obhut haben und Beiträge geltend machen |
| `Household`, Rolle `partner` (max. 1) | KiBV 8.1b | Partner/in in gefestigter Lebensgemeinschaft, die **nicht** erziehungsberechtigt ist. Diese Rolle fehlt in der Vorlage noch |
| `Household`, Rolle `kind` (beliebig viele) | KiBG 4.3 | Die betreuten Kinder |

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
| Art. 3.2 a–d | Anerkannte Einrichtungstypen | Variable, Eingabe (Kategorie) | `kibg_einrichtungstyp`: `kita` / `tagesfamilie` / `schulergaenzend` / `sonderschule` / `keine` | Welcher Ansatz gilt für Typ d? (O11) |
| Art. 3.2 (Kriterien) | Bewilligung, Qualitätskonzept, Leistungsvereinbarung | Variable, Eingabe (ja/nein) | `kibg_einrichtung_anerkannt` | Behördlicher Entscheid, daher Eingabe |
| Art. 3.3 | Bei der kantonalen Stelle angemeldet | Variable, Eingabe (ja/nein) | `kibg_einrichtung_angemeldet` | Beginn gemäss KiBV 6 |
| Art. 4.1 | Zivilrechtlicher Wohnsitz im Kanton | Variable, Eingabe (ja/nein) | `wohnsitz_kanton_sg` (Person) | Welcher Elternteil muss hier wohnen? (O8) |
| Art. 4.1 | Selbständig oder unselbständig erwerbstätig, mit Beschäftigungsgrad | Variable, Eingabe (%) | `beschaeftigungsgrad` (Person) | — |
| Art. 4.1a | Mindestens 20 Prozent | Parameter | `kibg.anspruch.min_beschaeftigungsgrad = 20` | — |
| Art. 4.1b | Zusammen mindestens 120 Prozent bei gemeinsamem Haushalt | Parameter + Eingabe | `kibg.anspruch.min_beschaeftigungsgrad_gemeinsam = 120`, `gemeinsamer_haushalt` (Haushalt) | Braucht zusätzlich jeder Elternteil 20 %? (O3) |
| Art. 4.1 | Beschäftigungsbedingung erfüllt | Variable, Formel | `kibg_beschaeftigung_erfuellt` (Haushalt) | a für einen Elternteil, b für einen gemeinsamen Haushalt |
| Art. 4.2 | Ausnahme in begründeten Fällen | Variable, Eingabe (ja/nein) | `kibg_ausnahme_bewilligt` | Menschlicher Entscheid; Gründe in KiBV 12 |
| Art. 4.3 | Ab drei Monaten | Parameter + Eingabe | `kibg.anspruch.mindestalter_monate = 3`, `geburtsdatum` | — |
| Art. 4.3 | Bis zum Abschluss der Primarschule | Variable, Eingabe (ja/nein) | `primarschule_abgeschlossen` (Kind) | Eine Tatsache, kein Alter |
| Art. 4 | Anspruch gesamt | Variable, Formel | `kibg_anspruch` (Kind) | Wohnsitz UND (Beschäftigung ODER Ausnahme) UND Alter UND Einrichtung |
| Art. 5.1–5.2 | Abhängig von massgebendem Einkommen und Vermögen (ME) | Variable | `kibg_massgebendes_einkommen` (Haushalt, jährlich) | Zusammengesetzt gemäss KiBV 8–11 |
| Art. 5.3 | Grundlage: letzte definitive Steuerveranlagung | Variable, Eingabe | `me_steuerveranlagung` (Person, jährlich) | In einem anderen Erlass definiert, der V EG-KVG (O5) |
| Art. 5.4 | Wesentliche Veränderung, daher aktuelle Gegebenheiten | Variable, Eingabe + Formel | `me_aktuell` (Person) | Schwelle in KiBV 11 |
| Art. 6.1 | Lineares Modell | Variable, Formel | `kibg_beitrag_pro_stunde` | Formel im Anhang der KiBV |
| Art. 6.2 | Beitrag höchstens so hoch wie die tatsächlichen Kosten | Variable, Eingabe + Formel | `kibg_betreuungskosten` (Kind, monatlich), `kibg_mindestbeitrag` | min(Beitrag, Kosten) |

### III. Plattform

| Ref. | Inhalt | Konzept | Bemerkung |
|---|---|---|---|
| Art. 7 | Gemeinsame elektronische Plattform | Nicht berechenbar | — |
| Art. 8.1–8.2 | Datenbearbeitung, auch besonders schützenswerter Daten | Nicht berechenbar | Wichtig für den Teil zu Ethik und Datenschutz |

### IV. Verfahren

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 9.1 | Beiträge nur auf Gesuch | Variable, Eingabe (Datum) | `gesuchsdatum` | — |
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
| Art. 20.1 | Beiträge nach Art. 6/17/18 sind Mindestbeiträge | Variable, Formel | `kibg_mindestbeitrag` | — |
| Art. 20.2 | Gemeinde kann mit Zusatzbeiträgen aufstocken | Variable, Eingabe | `gemeinde_z1`, `gemeinde_z2` (Haushalt, Fr./Stunde) | Werte pro Gemeinde unbekannt, daher Eingaben |
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
| Art. 2 | Zuständige Gemeinde: Wohnsitz der anspruchsberechtigten Eltern | Variable, Eingabe | `wohngemeinde` (Haushalt) | Bestimmt Z1/Z2. Getrennte Eltern in verschiedenen Gemeinden? (O8) |

### II. Anmeldung von Einrichtungen

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 3–5 | Anmeldung, Inhalt, Prüfung | Nicht berechenbar | — | Vereinfacht zu `kibg_einrichtung_angemeldet` |
| Art. 6 | Teilnahme beginnt am Ersten des Folgemonats nach der Bestätigung | Variable, Formel (optional) | `einrichtung_teilnahmebeginn` | Kann weggelassen werden |

### III. Anspruch und Bemessung

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 7 | Nur für Tage mit faktischer Obhut **und** genutzter Betreuung | Variable, Eingabe | `betreuungstage_mit_obhut` (Kind, monatlich) | Wichtig bei alternierender Obhut |
| Art. 8.1a | Gemeinsamer Haushalt: Einkommen beider Eltern | Variable, Formel | Teil von `kibg_massgebendes_einkommen` | Summe über Rolle `erziehungsberechtigt` |
| Art. 8.1b | Getrennter Haushalt: Gesuchsteller/in + gefestigte Partnerin oder gefestigter Partner, die oder der nicht erziehungsberechtigt ist | Variable, Formel | Teil von `kibg_massgebendes_einkommen` | Braucht Rolle `partner` |
| Art. 8.2a | Gefestigt = Ehe oder eingetragene Partnerschaft | Variable, Eingabe | `verheiratet_oder_eingetragen` | — |
| Art. 8.2b | Gefestigt = seit mindestens zwei Jahren gemeinsamer Haushalt (Konkubinat) | Parameter + Eingabe | `kibg.einkommen.mindestdauer_konkubinat_jahre = 2`, `beginn_gemeinsamer_haushalt` | — |
| Art. 8.2 | Gefestigte Lebensgemeinschaft | Variable, Formel | `gefestigte_lebensgemeinschaft` | a ODER b |
| Art. 9 | Ordentlich Besteuerte: ME nach Art. 12 Abs. 2 V EG-KVG | Variable, Eingabe | `me_steuerveranlagung` | Externer Erlass (O5) |
| Art. 10.1 | Quellenbesteuerte oder ohne Veranlagung: nach Art. 12bis V EG-KVG | Variable, Eingabe (Kategorie) | `besteuerungsart` | Externer Erlass (O5) |
| Art. 10.2 | Einkommens- und Vermögensnachweise einreichen | Nicht berechenbar | — | — |
| Art. 11.1 | Aktuelle Gegebenheiten nur auf Antrag | Variable, Eingabe (ja/nein) | `antrag_aktuelle_gegebenheiten` | — |
| Art. 11.2 | Abweichung von mindestens 25 % bei Gesuchstellung | Parameter + Formel | `kibg.einkommen.schwelle_abweichung = 0.25`, `kibg_massgebendes_einkommen` | Nach oben und unten? (O12) |
| Art. 11.3 | Veränderung von mindestens 25 % während laufender Verfügung gilt ab dem Ersten des Folgemonats | Formel (optional) | — | Datumslogik, kann weggelassen werden |
| Art. 12 a–c | Ausnahmegründe: berufliche Integration, familiäre Belastung, Indikation beim Kind | Variable, Eingabe (Kategorie) | `kibg_ausnahmegrund` | Dokumentiert den Grund; der Entscheid bleibt bei `kibg_ausnahme_bewilligt` |

### IV. Berechnung

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 13 | Formel im Anhang | Variable, Formel | `kibg_beitrag_pro_stunde` | — |
| Art. 14.1a | Unter 18 Monaten, Kita: Fr. 11.00 | Parameter | `kibg.hoechstbeitrag.unter_18_monate.kita = 11.00` | Grenze bei genau 18 Monaten (O2) |
| Art. 14.1b | Unter 18 Monaten, Tagesfamilie: Fr. 8.30 | Parameter | `…unter_18_monate.tagesfamilie = 8.30` | — |
| Art. 14.2a | Über 18 Monaten bis Einschulung, Kita: Fr. 7.50 | Parameter | `…ab_18_monate.kita = 7.50` | — |
| Art. 14.2b | Über 18 Monaten bis Einschulung, Tagesfamilie: Fr. 5.50 | Parameter | `…ab_18_monate.tagesfamilie = 5.50` | — |
| Art. 14.3a | Eingeschult bis Ende Primarstufe, Kita: Fr. 7.50 | Parameter | `…eingeschult.kita = 7.50` | — |
| Art. 14.3b | Eingeschult, schulergänzende Betreuung: Fr. 5.50 | Parameter | `…eingeschult.schulergaenzend = 5.50` | — |
| Art. 14.3c | Eingeschult, Tagesfamilie: Fr. 5.50 | Parameter | `…eingeschult.tagesfamilie = 5.50` | — |
| Art. 14.1–3 | Welche Altersstufe gilt | Variable, Eingabe + Formel | `eingeschult` (ja/nein), `kibg_altersstufe` | Die Einschulung ist eine Tatsache, kein Alter |
| Art. 14.1–3 | Massgebender Höchstbeitrag | Variable, Formel | `kibg_hoechstbeitrag` (Kind) | Altersstufe × Einrichtungstyp |
| Art. 14.4 | Höchstens 12 subventionierte Stunden pro Tag | Parameter | `kibg.betreuung.max_stunden_pro_tag = 12` | — |
| Art. 14.4 | Höchstens 5 Tage pro Woche | Parameter | `kibg.betreuung.max_tage_pro_woche = 5` | — |
| Art. 14.4 | Subventionierte Stunden | Variable, Eingabe + Formel | `betreuungsstunden` (Kind, monatlich), `kibg_subventionierte_stunden` | Umrechnung Woche auf Monat (O7) |
| Art. 14.5 | Betreuungsmodule und Monatspauschalen per Richtlinien | Ausserhalb des Umfangs | — | Die Richtlinien liegen nicht vor (O7) |
| Art. 15.1 | Kleinstes ME Fr. 40'000; bis dahin voller Beitrag | Parameter + Formel | `kibg.einkommen.min = 40_000` | Faktor nach oben begrenzt |
| Art. 15.2 | Höchstes ME Fr. 154'000; darüber kein Beitrag | Parameter + Formel | `kibg.einkommen.max = 154_000` | Was gilt hier für Z2? (O4) |

### V. Verfahren für die Ausrichtung der Beiträge

| Ref. | Inhalt | Konzept | Vorgeschlagener Name | Bemerkung |
|---|---|---|---|---|
| Art. 16.1 | Kita und Tagesfamilie: 12 Monate, im Jahr der Einschulung bis Schuljahresbeginn | Formel (optional) | `kibg_verfuegung_ende` | — |
| Art. 16.2 | Eingeschulte Kinder: ein Schuljahr, oder bis zum Ende des laufenden | Formel (optional) | `kibg_verfuegung_ende` | Datum des Schuljahresbeginns fehlt im Text (O9) |
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
| Begrenzung auf 0–1 | Formel | KiBV 15, die Formel selbst begrenzt nicht |

**Hinweis zur Modellierung:** B in zwei Teile aufteilen. Der Mindestbeitrag ist MaxV × Faktor und wird von Kanton und Gemeinde je hälftig getragen (KiBG 18). Der Zusatzbeitrag ist Z1 × Faktor + Z2 und wird von der Gemeinde allein bezahlt (KiBG 20.2). So ergibt sich auch die Aufteilung der Finanzierung.

**Berechnungskette:**

1. Anspruch
2. massgebendes Einkommen (ME)
3. Höchstbeitrag
4. Beitrag pro Stunde
5. × subventionierte Stunden
6. auf die Kosten begrenzt
7. aufgeteilt auf Kanton, Gemeinde und Restkosten der Eltern

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
| O1 | Kein Vollzugsbeginn («ab ●●»). Ein Platzhalterdatum wählen | KiBG IV.1, KiBV IV |
| O2 | Ein Kind mit genau 18 Monaten fällt zwischen «unter 18» und «über 18» | KiBV 14.1–14.2 |
| O3 | Braucht es bei 120 % zusammen zusätzlich mindestens 20 % pro Elternteil? Und gilt «a» nur für Alleinerziehende? | KiBG 4.1 |
| O4 | Gilt Z2 (einkommensunabhängig) auch über Fr. 154'000? | KiBV 15.2 vs. Anhang |
| O5 | Das massgebende Einkommen ist in einem anderen Erlass definiert (V EG-KVG, sGS 331.111), der in den Unterlagen fehlt. Text beschaffen oder Einkommen als Eingabe behandeln | KiBV 9–10 |
| O6 | Das Gesetzes-PDF ist die **Fassung der ersten Lesung (16. September 2025)**, die KiBV verweist aber auf das Gesetz vom 14. Juni 2026. Bei den Organisatoren nachfragen, ob der Schlusstext abweicht | KiBG Titelseite |
| O7 | Umrechnung der Wochenobergrenzen auf einen Monat; Betreuungsmodule und Monatspauschalen sind Richtlinien überlassen, die nicht öffentlich sind | KiBV 14.4–14.5 |
| O8 | Welcher Elternteil muss im Kanton wohnen, und welche Gemeinde ist zuständig, wenn die Eltern getrennt leben? | KiBG 4.1, KiBV 2 |
| O9 | Das Datum des Schuljahresbeginns steht nicht im Text | KiBV 16.2 |
| O10 | Getrennte Eltern mit alternierender Obhut: Wer stellt das Gesuch, und wie werden die Tage aufgeteilt? | KiBV 7, 8.1b |
| O11 | Private Sonderschulen (KiBG 3.2d): vermutlich der Ansatz für schulergänzende Betreuung von Fr. 5.50? | KiBG 3.2d, KiBV 14.3 |
| O12 | Zählt die Abweichung von 25 % in beide Richtungen (nach oben und unten)? | KiBV 11.2–11.3 |

---

## Vorgeschlagene Reihenfolge für das Programmieren

1. Zuerst der Kern: Anspruch (KiBG 3–4), massgebendes Einkommen (KiBV 8 und 11), die Formel mit Ansätzen und Grenzen (KiBV 13–15, Anhang), die Stundenobergrenzen und die Kostenobergrenze.
2. Danach die Aufteilung der Finanzierung und die Restkosten.
3. Optional: die Datumsregeln (KiBG 9.2, KiBV 16, 25) und die Budgetsimulation (KiBG 17).
