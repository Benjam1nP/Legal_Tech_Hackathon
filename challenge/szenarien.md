# Szenarien KiBG / KiBV (Eingaben und erwartete Ergebnisse)

Dieser Katalog beschreibt konkrete Familien und Grenzfälle mit den Beträgen, die der Rechner liefern muss. Die erwarteten Ergebnisse sind **von Hand aus dem Gesetz gerechnet**, nicht aus dem Code. So prüfen die Tests, ob der Code das Gesetz richtig umsetzt.

Verwendung:

- **Tests:** Jedes Szenario wird ein OpenFisca-Test (Beispiel im Anhang).
- **Frontend und Pitch:** Die Personas (Teil 1) sind die Beispielfamilien für die Demo.
- **Stellungnahme zur Verordnung:** Die Auslegungsfälle (Teil 4) und die unklaren Stellen (Teil 7) zeigen an konkreten Zahlen, wo der Text unklar ist und wie wir ihn auslegen.

Die Variablennamen stammen aus `line-to-line-rules.md`, Abschnitt «Variablen: Entität und Periode».

**Status je Szenario**

- **fest:** folgt eindeutig aus dem Text.
- **Annahme A…:** hängt von einer Annahme ab, die das Team getroffen hat, weil der Text schweigt (siehe unten).
- **Entscheid O…:** hängt von einer Auslegungsfrage ab, die das Team entschieden hat (siehe `line-to-line-rules.md`, offene Fragen).

**Abdeckung:** Die Übersicht am Schluss zeigt, welche Bestimmung durch welche Fälle geprüft wird.

---

## Grundlagen

### Formel und Werte

**Beitrag pro Stunde B = (MaxV + Z1) × F + Z2**, mit dem Einkommensfaktor **F** (`kibg_einkommensfaktor`) **= 1 − (ME − 40'000) / 114'000**, begrenzt auf 0 bis 1 (KiBV 13, 15, Anhang).

| Einkommen ME | Faktor F | Merkhilfe |
|---|---|---|
| bis 40'000 | 1 | voller Beitrag |
| 51'400 | 0.9 | |
| 68'500 | 0.75 | |
| 97'000 | 0.5 | genau in der Mitte |
| 125'500 | 0.25 | |
| ab 154'000 | 0 | kein Beitrag |

| Höchstbeitrag MaxV (Fr. pro Stunde) | Kita | Tagesfamilie | Schulergänzend |
|---|---|---|---|
| unter 18 Monaten (KiBV 14.1) | 11.00 | 8.30 | — |
| über 18 Monaten bis Einschulung (KiBV 14.2) | 7.50 | 5.50 | — |
| eingeschult bis Ende Primarstufe (KiBV 14.3) | 7.50 | 5.50 | 5.50 |

Für Kita und Tagesfamilie sind die Ansätze vor und nach der Einschulung gleich. Ob ein Kind eingeschult ist, spielt deshalb nur für die schulergänzende Betreuung eine Rolle.

**Rechenweg pro Kind und Monat**

1. Anspruch prüfen (KiBG 3–4). Kein Anspruch → alle Beiträge 0; die Eltern tragen die vollen Kosten.
2. Subventionierte Stunden = min(Betreuungsstunden, Betreuungstage × 12) (KiBV 14.4).
3. Mindestbeitrag = MaxV × F × subventionierte Stunden, auf 5 Rappen gerundet, höchstens die Kosten (KiBG 6.2, A4).
4. Zusatzbeitrag = (Z1 × F + Z2) × subventionierte Stunden, auf 5 Rappen gerundet, höchstens Kosten − Mindestbeitrag (KiBG 20.3, A2, A4).
5. Beitrag total = Mindestbeitrag + Zusatzbeitrag.
6. Restkosten der Eltern = Kosten − Beitrag total (KiBG 12.2).
7. Anteil Kanton = Mindestbeitrag / 2, auf 5 Rappen gerundet; Anteil Gemeinde = Mindestbeitrag − Anteil Kanton + Zusatzbeitrag (KiBG 18.1, 20.2).

### Standardwerte

Wenn bei einem Szenario nichts anderes steht, gilt:

- Monat: **2028-09** (Vollzugsbeginn als Platzhalter: 1. August 2028)
- Alle Erwachsenen haben Wohnsitz im Kanton St. Gallen.
- Einrichtung anerkannt und angemeldet; Kind nicht eingeschult, Primarschule nicht abgeschlossen.
- Keine Zusatzbeiträge der Gemeinde (`kibg_zusatzbeitrag_z1` = `kibg_zusatzbeitrag_z2` = 0); keine Ausnahme nach KiBG 4.2; kein Antrag auf aktuelle Gegebenheiten.
- Massgebendes Einkommen als Eingabe für das Jahr 2028.
- Jedes Kind: Betreuungsbeginn **2028-08-01**, Gesuch wird am **2028-08-15** abgegeben. Das liegt in der Übergangsfrist; die Beiträge beginnen am 2028-08-01. Beide Daten sind Pflicht (siehe F10, F11).
- Bei getrennt lebenden Eltern enthält der Haushalt im Modell nur die gesuchstellende Person (und allenfalls ihre Partnerin oder ihren Partner).
- Bei zwei Erziehungsberechtigten im Haushalt stellt die Mutter das Gesuch (`kibg_gesuchstellend`). Diese Angabe ist Pflicht (siehe F2).
- Jedes Kind hat ein Geburtsdatum. Diese Angabe ist Pflicht (siehe F1).

### Annahmen

| Nr. | Annahme | Grund | Betrifft | Stand |
|---|---|---|---|---|
| A1 | Alter des Kindes und Dauer einer Lebensgemeinschaft werden am **ersten Tag des Monats** bestimmt und gelten für den ganzen Monat | Der Beitrag wird pro Monat berechnet; der Text sagt nichts zum Stichtag | G7–G8, G15–G17, G41–G42, G49, G51, Q1 | bestätigt |
| A2 | Übersteigen Mindest- und Zusatzbeitrag die Kosten, wird **zuerst der Zusatzbeitrag** gekürzt | KiBG 6.2 begrenzt schon den Mindestbeitrag auf die Kosten; KiBG 20.3 begrenzt dann die Summe | P6b, G24 | bestätigt |
| A3 | Die Grenze von 5 Tagen pro Woche wird nicht geprüft (Teamentscheid, siehe Dokumentation) | Eingaben sind Monatswerte | E1 | bestätigt |
| A4 | Beträge in Franken werden **kaufmännisch auf 5 Rappen gerundet** (ab 2.5 Rappen auf, sonst ab). Gerundet werden die Monatsbeträge (Mindest- und Zusatzbeitrag, Anteil Kanton), nicht der Beitrag pro Stunde. Die Kostenobergrenze gilt nach dem Runden. Der Anteil der Gemeinde ist der Rest, damit die Summe stimmt. Die Restkosten der Eltern sind Kosten minus Beitrag, ohne weitere Rundung | Der Text regelt keine Rundung; 5 Rappen ist die kleinste Münze | G25–G29 | bestätigt |
| A5 | Die eingegebenen Stunden und Tage sind nur solche mit faktischer Obhut (KiBV 7) | Vereinfachung der Eingabe | alle | bestätigt |
| A6 | Beschäftigungsgrad: Jeder Elternteil braucht mindestens 20 % (KiBG 4.1a); Eltern im gemeinsamen Haushalt zusätzlich zusammen mindestens 120 % (KiBG 4.1b) | Entscheid zu O3: lit. a und b gelten kumulativ | G30–G38, X6, Q2 | bestätigt |
| A7 | **Fristen:** Eine Frist in Tagen beginnt am Tag nach dem Ereignis; eine Frist in Monaten endet am Tag mit derselben Zahl (sinngemäss Art. 77 OR) | Der Text regelt die Berechnung nicht | D1–D2, D7 | bestätigt |
| A8 | **Eingeschult** ist ein Kind ab dem Eintritt in den obligatorischen Kindergarten | KiBV 16.1 knüpft an das Jahr an, in dem das Kind «schulpflichtig wird»; im Kanton St. Gallen beginnt die Schulpflicht mit dem Kindergarten | G14 | bestätigt |
| A9 | Im Monat, in dem die Beiträge beginnen, geben die Eltern **nur die Betreuungstage und -stunden ab diesem Tag** ein. Vor dem Beitragsbeginn gibt es keinen Anspruch | KiBG 9.2: Beiträge «ab dem Zeitpunkt der Gesuchstellung»; der Rechner rechnet pro Monat | D4, D5, F13 | bestätigt |
| A10 | Das **Gesuchsdatum** ist der Tag, an dem das Gesuch **abgegeben** wird (bei der Gemeinde oder durch Postaufgabe). Es ist Pflicht, ebenso der Betreuungsbeginn | Nach Verwaltungsrecht wahrt die Abgabe die Frist, nicht erst der Eingang (Entscheid des Rechtsteams) | D1–D7, D10–D11, F10–F11 | bestätigt |
| A11 | Die **Beitragsverfügung beginnt mit dem Beitragsbeginn**; auch Übergangsgesuche nach KiBV 25.1 (KiBV 25.2: KiBV 16 gilt sachgemäss). Der Text knüpft an das Datum der Verfügung an, das der Rechner nicht kennt | Vorläufig, Rechtsteam bestätigen | D12–D19 | **neu, bitte prüfen** |
| A12 | Endet die Verfügung mitten im Monat, geben die Eltern **nur die Betreuungstage bis zu diesem Tag** an; mehr Tage, als bis dahin im Monat liegen, sind ein Eingabefehler (wie A9 am Beginn). Ohne Angabe des Kindergartenjahres gilt für die Wahl zwischen KiBV 16.1 und 16.2 «eingeschult» im berechneten Monat | Der Rechner rechnet pro Monat | D14, F14–F15 | **neu, bitte prüfen** |

---

## Teil 1: Personas

### P1 – Paar, ein Kleinkind in der Kita (Grundfall)

| Eingabe | Wert |
|---|---|
| Haushalt | Mutter und Vater, gemeinsamer Haushalt |
| Mutter | Pensum 100 %, Einkommen 60'000 |
| Vater | Pensum 40 %, Einkommen 37'000 |
| Kind Lina | geboren 2027-09-01 (12 Monate), Kita |
| Betreuung | 8 Tage, 80 Stunden (2 Tage pro Woche à 10 Stunden) |
| Kosten | 1'040 (80 × 13.00) |

**Rechnung**

- Anspruch: beide mindestens 20 % ✓ und zusammen 140 % ≥ 120 % ✓; Kind mindestens 3 Monate alt ✓
- Einkommen: 60'000 + 37'000 = 97'000 (KiBV 8.1a) → F = 0.5
- MaxV: unter 18 Monaten, Kita = 11.00 → B = 5.50
- Stunden: min(80, 8 × 12 = 96) = 80
- Mindestbeitrag: 5.50 × 80 = 440 (≤ 1'040 ✓)

| Ergebnis | Erwartet |
|---|---|
| `kibg_anspruch` | ja |
| `kibg_massgebendes_einkommen` | 97'000 |
| `kibg_einkommensfaktor` | 0.5 |
| `kibg_hoechstbeitrag` | 11.00 |
| `kibg_beitrag_pro_stunde` | 5.50 |
| `kibg_subventionierte_stunden` | 80 |
| `kibg_mindestbeitrag` | 440.00 |
| `kibg_zusatzbeitrag` | 0.00 |
| `kibg_beitrag_total` | 440.00 |
| `kibg_restkosten_eltern` | 600.00 |
| `kibg_anteil_kanton` | 220.00 |
| `kibg_anteil_gemeinde` | 220.00 |

Quelle: KiBG 4, 6, 12.2, 18.1; KiBV 8, 13–15, Anhang. **Status: fest.**

### P2 – Alleinerziehende Mutter, Tagesfamilie, tiefes Einkommen

| Eingabe | Wert |
|---|---|
| Haushalt | Mutter allein |
| Mutter | Pensum 50 %, Einkommen 30'000 |
| Kind Noah | geboren 2026-03-01 (30 Monate), Tagesfamilie |
| Betreuung | 12 Tage, 108 Stunden (3 Tage pro Woche à 9 Stunden) |
| Kosten | 1'134 (108 × 10.50) |

**Rechnung**

- Anspruch: 50 % ≥ 20 % ✓
- Einkommen 30'000 liegt unter 40'000 → F = 1 (KiBV 15.1)
- MaxV: über 18 Monaten, Tagesfamilie = 5.50 → B = 5.50
- Mindestbeitrag: 5.50 × 108 = 594

| Ergebnis | Erwartet |
|---|---|
| `kibg_einkommensfaktor` | 1 |
| `kibg_beitrag_pro_stunde` | 5.50 |
| `kibg_beitrag_total` | 594.00 |
| `kibg_restkosten_eltern` | 540.00 |
| `kibg_anteil_kanton` | 297.00 |
| `kibg_anteil_gemeinde` | 297.00 |

Quelle: KiBG 4.1a; KiBV 14.2b, 15.1. **Status: fest.**

### P3 – Paar, Baby in der Kita und Schulkind in der Tagesstruktur

| Eingabe | Wert |
|---|---|
| Haushalt | Mutter und Vater, gemeinsamer Haushalt |
| Mutter / Vater | Pensum 80 % / 60 %, Einkommen 40'000 / 28'500 |
| Kind Mia | geboren 2028-03-01 (6 Monate), Kita, 12 Tage, 120 Stunden, Kosten 1'500 (120 × 12.50) |
| Kind Leo | geboren 2021-05-01 (7 Jahre), eingeschult, schulergänzende Betreuung, 16 Tage, 48 Stunden, Kosten 432 (48 × 9.00) |

**Rechnung**

- Anspruch: beide mindestens 20 %, zusammen 140 % ✓
- Einkommen 68'500 → F = 0.75
- Mia: 11.00 × 0.75 = 8.25 pro Stunde × 120 = 990
- Leo: 5.50 × 0.75 = 4.125 pro Stunde × 48 = 198

| Ergebnis | Mia | Leo | Familie |
|---|---|---|---|
| `kibg_beitrag_pro_stunde` | 8.25 | 4.125 | — |
| `kibg_beitrag_total` | 990.00 | 198.00 | 1'188.00 |
| `kibg_restkosten_eltern` | 510.00 | 234.00 | 744.00 |
| `kibg_anteil_kanton` | 495.00 | 99.00 | 594.00 |
| `kibg_anteil_gemeinde` | 495.00 | 99.00 | 594.00 |

Quelle: KiBV 14.1a, 14.3b. **Status: fest.** Zeigt: zwei Kinder, zwei Ansätze, gleicher Faktor. Der Beitrag pro Stunde von Leo (4.125) wird nicht gerundet; erst der Monatsbetrag (198.00).

### P4 – Paar mit hohem Einkommen

| Eingabe | Wert |
|---|---|
| Haushalt | gemeinsamer Haushalt, Pensum 100 % / 100 %, Einkommen 70'000 / 55'500 |
| Kind Elias | geboren 2026-09-01 (24 Monate), Kita, 20 Tage, 200 Stunden, Kosten 2'800 (200 × 14.00) |

**Rechnung**

- Einkommen 125'500 → F = 0.25
- MaxV über 18 Monaten, Kita = 7.50 → B = 1.875
- Beitrag: 1.875 × 200 = 375

| Ergebnis | Erwartet |
|---|---|
| `kibg_beitrag_pro_stunde` | 1.875 |
| `kibg_beitrag_total` | 375.00 |
| `kibg_restkosten_eltern` | 2'425.00 |
| `kibg_anteil_kanton` / `kibg_anteil_gemeinde` | 187.50 / 187.50 |

Quelle: KiBV 14.2a, 15. **Status: fest.**

### P5 – Wie P1, aber die Gemeinde zahlt Zusatzbeiträge

Eingaben wie P1, zusätzlich `kibg_zusatzbeitrag_z1` = **2.00** und `kibg_zusatzbeitrag_z2` = **1.00** pro Stunde.

**Rechnung**

- B = (11.00 + 2.00) × 0.5 + 1.00 = 7.50
- Davon Mindestbeitrag: 11.00 × 0.5 = 5.50 pro Stunde → 440
- Davon Zusatzbeitrag: 2.00 × 0.5 + 1.00 = 2.00 pro Stunde → 160
- Summe 600 ≤ Kosten 1'040 ✓

| Ergebnis | Erwartet |
|---|---|
| `kibg_beitrag_pro_stunde` | 7.50 |
| `kibg_mindestbeitrag` | 440.00 |
| `kibg_zusatzbeitrag` | 160.00 |
| `kibg_beitrag_total` | 600.00 |
| `kibg_restkosten_eltern` | 440.00 |
| `kibg_anteil_kanton` | 220.00 |
| `kibg_anteil_gemeinde` | 380.00 (220 + 160) |

Quelle: KiBG 18.1, 20; KiBV 24, Anhang. **Status: fest.**

### P6 – Günstige Kita: Kostenobergrenze greift

| Eingabe | Wert |
|---|---|
| Haushalt | Vater allein, Pensum 60 %, Einkommen 40'000 |
| Kind Sara | geboren 2028-01-01 (8 Monate), Kita, 10 Tage, 100 Stunden, Kosten 900 (100 × 9.00) |

**Rechnung**

- F = 1 → B = 11.00 → ungekürzt 1'100
- Kosten nur 900 → Mindestbeitrag = 900 (KiBG 6.2)

| Ergebnis | Erwartet |
|---|---|
| `kibg_mindestbeitrag` | 900.00 |
| `kibg_beitrag_total` | 900.00 |
| `kibg_restkosten_eltern` | 0.00 |
| `kibg_anteil_kanton` / `kibg_anteil_gemeinde` | 450.00 / 450.00 |

**Status: fest.**

### P6b – Wie P6, Kosten 1'300 (100 × 13.00), Z1 = 2.00, Z2 = 1.00

**Rechnung**

- Mindestbeitrag: 11.00 × 1 × 100 = 1'100 (≤ 1'300 ✓)
- Zusatzbeitrag ungekürzt: (2.00 × 1 + 1.00) × 100 = 300
- Summe 1'400 > Kosten 1'300 → Zusatzbeitrag auf 200 gekürzt (A2)

| Ergebnis | Erwartet |
|---|---|
| `kibg_mindestbeitrag` | 1'100.00 |
| `kibg_zusatzbeitrag` | 200.00 |
| `kibg_beitrag_total` | 1'300.00 |
| `kibg_restkosten_eltern` | 0.00 |
| `kibg_anteil_kanton` / `kibg_anteil_gemeinde` | 550.00 / 750.00 |

Quelle: KiBG 6.2, 20.3. **Status: Annahme A2.**

### P7 – Getrennter Vater mit neuer Partnerin (Konkubinat)

| Eingabe | Wert |
|---|---|
| Haushalt | Vater (erziehungsberechtigt, stellt das Gesuch) und Partnerin (nicht erziehungsberechtigt); die Mutter lebt in einem anderen Haushalt |
| Vater | Pensum 80 %, Einkommen 51'400 |
| Partnerin | Pensum 100 %, Einkommen 45'600; gemeinsamer Haushalt seit 2026-01-01, nicht verheiratet |
| Kind Jonas | geboren 2024-09-01 (4 Jahre), Kita, 8 Tage, 72 Stunden (nur die Obhutstage beim Vater), Kosten 864 (72 × 12.00) |

**Rechnung**

- Anspruch: Vater 80 % ≥ 20 % ✓. Das Pensum der Partnerin zählt nicht, weil sie nicht erziehungsberechtigt ist (KiBG 4.1)
- Konkubinat seit mehr als zwei Jahren → gefestigte Lebensgemeinschaft (KiBV 8.2b) → Einkommen der Partnerin zählt (KiBV 8.1b)
- Einkommen 51'400 + 45'600 = 97'000 → F = 0.5
- MaxV über 18 Monaten, Kita = 7.50 → B = 3.75 → 3.75 × 72 = 270

| Ergebnis | Erwartet |
|---|---|
| `kibg_gefestigte_lebensgemeinschaft` | ja |
| `kibg_massgebendes_einkommen` | 97'000 |
| `kibg_beitrag_total` | 270.00 |
| `kibg_restkosten_eltern` | 594.00 |
| `kibg_anteil_kanton` / `kibg_anteil_gemeinde` | 135.00 / 135.00 |

Quelle: KiBV 7, 8. **Status: fest.**

### P7b – Wie P7, aber Konkubinat erst seit 2027-06-01

**Rechnung**

- Erst 1 Jahr und 3 Monate → keine gefestigte Lebensgemeinschaft → nur das Einkommen des Vaters zählt
- Einkommen 51'400 → F = 0.9 → B = 7.50 × 0.9 = 6.75 → 6.75 × 72 = 486

| Ergebnis | Erwartet |
|---|---|
| `kibg_gefestigte_lebensgemeinschaft` | nein |
| `kibg_massgebendes_einkommen` | 51'400 |
| `kibg_beitrag_total` | 486.00 |
| `kibg_restkosten_eltern` | 378.00 |
| `kibg_anteil_kanton` / `kibg_anteil_gemeinde` | 243.00 / 243.00 |

**Status: fest.** Zeigt: Dieselbe Familie erhält fast doppelt so viel, solange das Konkubinat jünger als zwei Jahre ist.

---

## Teil 2: Grenzfälle

Alle Grenzfälle gehen von **P1** aus, wenn nichts anderes steht; angegeben ist nur, was sich ändert.

### Einkommen (KiBV 15, Anhang)

Das ganze Einkommen liegt bei der Mutter, der Vater hat 0.

| Nr. | Einkommen | `kibg_einkommensfaktor` | `kibg_beitrag_pro_stunde` | `kibg_mindestbeitrag` | Status |
|---|---|---|---|---|---|
| G1 | 39'999 | 1 (begrenzt, sonst > 1) | 11.00 | 880.00 | fest |
| G2 | 40'000 | 1 | 11.00 | 880.00 | fest |
| G3 | 68'500 | 0.75 | 8.25 | 660.00 | fest |
| G4 | 125'500 | 0.25 | 2.75 | 220.00 | fest |
| G5 | 154'000 | 0 | 0.00 | 0.00 (Anspruch ja) | fest |
| G6 | 154'001 | 0 (begrenzt, sonst negativ) | 0.00 | 0.00, nicht negativ | fest |

### Altersstufe und Einrichtungstyp (KiBV 14.1–14.3)

| Nr. | Änderung | MaxV | `kibg_beitrag_pro_stunde` | `kibg_mindestbeitrag` | Status |
|---|---|---|---|---|---|
| G7 | geboren 2027-03-02 (am 1. September 17 Monate und 30 Tage) | 11.00 | 5.50 | 440.00 | A1 |
| G8 | geboren 2027-02-28 (über 18 Monate) | 7.50 | 3.75 | 300.00 | A1 |
| G9 | Tagesfamilie, 12 Monate | 8.30 | 4.15 | 332.00 | fest |
| G10 | Tagesfamilie, geboren 2026-03-01 (30 Monate) | 5.50 | 2.75 | 220.00 | fest |
| G11 | Kita, eingeschult (geboren 2022-05-01) | 7.50 | 3.75 | 300.00 | fest |
| G12 | schulergänzende Betreuung, eingeschult (wie G11) | 5.50 | 2.75 | 220.00 | fest |
| G13 | Tagesfamilie, eingeschult (wie G11) | 5.50 | 2.75 | 220.00 | fest |
| G14 | Kindergartenkind, geboren 2023-05-01 (5 Jahre), schulergänzende Betreuung, eingeschult | 5.50 | 2.75 | 220.00 | A8 |

Genau 18 Monate (geboren 2027-03-01): siehe Q1, Ergebnis 7.50.

### Mindestalter (KiBG 4.3)

| Nr. | Änderung | `kibg_alter_erfuellt` | `kibg_beitrag_total` | Status |
|---|---|---|---|---|
| G15 | geboren 2028-06-01 (genau 3 Monate) | ja | 440.00 | A1 |
| G16 | geboren 2028-06-02 (noch keine 3 Monate) | nein | 0.00 (Restkosten 1'040) | A1 |
| G17 | wie G16, aber Monat 2028-10 (jetzt 3 Monate alt) | ja | 440.00 | A1 |

### Stunden (KiBV 14.4)

| Nr. | Änderung | `kibg_subventionierte_stunden` | `kibg_mindestbeitrag` | `kibg_restkosten_eltern` | Status |
|---|---|---|---|---|---|
| G18 | 10 Tage, 120 Stunden, Kosten 1'560 | 120 | 660.00 | 900.00 | fest |
| G19 | 10 Tage, 130 Stunden, Kosten 1'690 | 120 (nicht 130) | 660.00 | 1'030.00 | fest |
| G20 | 0 Tage, 0 Stunden, Kosten 0 | 0 | 0.00 (Anspruch ja) | 0.00 | fest |

### Kosten (KiBG 6.2, 20.3)

| Nr. | Änderung | `kibg_mindestbeitrag` | `kibg_zusatzbeitrag` | `kibg_restkosten_eltern` | Kanton / Gemeinde | Status |
|---|---|---|---|---|---|---|
| G21 | Kosten genau 440 | 440.00 | 0.00 | 0.00 | 220.00 / 220.00 | fest |
| G22 | Kosten 400 | 400.00 | 0.00 | 0.00 | 200.00 / 200.00 | fest |
| G23 | Kosten 0 (z. B. von der Gemeinde gratis angeboten) | 0.00 | 0.00 | 0.00 | 0.00 / 0.00 | fest |
| G24 | wie P6 (Kosten 900), dazu Z1 = 2.00, Z2 = 1.00 | 900.00 | 0.00 (kein Platz mehr unter den Kosten) | 0.00 | 450.00 / 450.00 | A2 |

### Rundung auf 5 Rappen (A4)

Wie P1 (Kita, unter 18 Monaten, 80 Stunden, Kosten 1'040), das ganze Einkommen bei der Mutter.

| Nr. | Änderung | ungerundet | `kibg_mindestbeitrag` | `kibg_zusatzbeitrag` | Kanton / Gemeinde | `kibg_restkosten_eltern` | Status |
|---|---|---|---|---|---|---|---|
| G25 | Einkommen 50'000 | 802.807 | 802.80 (abgerundet) | 0.00 | 401.40 / 401.40 | 237.20 | A4 |
| G26 | Einkommen 62'000 | 710.175 | 710.20 (aufgerundet) | 0.00 | 355.10 / 355.10 | 329.80 | A4 |
| G27 | Einkommen 83'000 | 548.070 | 548.05 | 0.00 | 274.05 / 274.00 (Hälfte 274.025 aufgerundet, Gemeinde erhält den Rest) | 491.95 | A4 |
| G28 | Einkommen 50'000, Kosten 802.78 | 802.807 | 802.78 (gerundet 802.80, dann auf die Kosten begrenzt) | 0.00 | 401.40 / 401.38 | 0.00 | A4 |
| G29 | Einkommen 50'000, Z1 = 2.00, Z2 = 1.00 | 802.807 + 225.965 | 802.80 | 225.95 | 401.40 / 627.35 | 11.25 | A4 |

Hinweis für den Code: Mit Gleitkommazahlen kann 274.025 intern als 274.02499… erscheinen und falsch abgerundet werden. Vor dem Runden auf ganze Rappen runden oder eine kleine Toleranz verwenden.

### Beschäftigungsgrad und Ausnahme (KiBG 4.1–4.2, KiBV 12)

lit. a und lit. b gelten kumulativ (Entscheid O3). lit. b ist nur bei gemeinsamem Haushalt anwendbar; sonst gilt sie als erfüllt. Die Ausnahme (KiBG 4.2) ersetzt den Beschäftigungsgrad, nicht die übrigen Voraussetzungen.

| Nr. | Änderung | lit. a: jede Person ≥ 20 % | lit. b: zusammen ≥ 120 % bei gemeinsamem Haushalt | `kibg_beschaeftigung_erfuellt` | `kibg_anspruch` | Status |
|---|---|---|---|---|---|---|
| G30 | Mutter allein, 20 % | ja | ja (nicht anwendbar) | ja | ja | A6 |
| G31 | Mutter allein, 19 % | nein | ja (nicht anwendbar) | nein | nein | A6 |
| G32 | Paar, 100 % + 20 % = 120 % | ja | ja | ja | ja | A6 |
| G33 | Paar, 100 % + 19 % = 119 % | nein | nein | nein | nein | A6 |
| G34 | Paar, 60 % + 60 % | ja | ja | ja | ja | A6 |
| G35 | Paar, 110 % + 10 % = 120 % | nein | ja | nein (Vater unter 20 %) | nein | Entscheid O3 |
| G36 | Paar, 100 % + 0 %, Ausnahme bewilligt (`kibg_ausnahme_bewilligt`) | nein | nein | nein | ja | fest |
| G37 | wie P2, aber Mutter 0 % (Stellensuche), Ausnahme bewilligt, Grund berufliche Integration (KiBV 12a) | nein | ja (nicht anwendbar) | nein | ja, Beitrag 594.00 | fest |
| G38 | wie P7, aber Partnerin 0 % | ja | ja (nicht anwendbar) | ja (nur der Vater zählt) | ja, Beitrag 270.00 | fest |

### Zusatzbeiträge (KiBG 20, KiBV 24)

| Nr. | Änderung | `kibg_mindestbeitrag` | `kibg_zusatzbeitrag` | Status |
|---|---|---|---|---|
| G39 | Einkommen 160'000, nur Z1 = 2.00 (einkommensabhängig) | 0.00 | 0.00 (Z1 wird mit F = 0 multipliziert) | fest |

Einkommen über 154'000 mit Z2: siehe Q3.

### Massgebendes Einkommen und Haushalt (KiBV 8)

| Nr. | Änderung | `kibg_gefestigte_lebensgemeinschaft` | `kibg_massgebendes_einkommen` | Status |
|---|---|---|---|---|
| G40 | P1, Eltern nicht verheiratet, gemeinsamer Haushalt erst seit 2028-03-01 | — (beide erziehungsberechtigt) | 97'000: beide Einkommen zählen ohne Mindestdauer (KiBV 8.1a) | fest |
| G41 | P7, Konkubinat seit 2026-09-01 (genau 2 Jahre) | ja | 97'000 | A1 |
| G42 | P7, Konkubinat seit 2026-09-02 | nein | 51'400 | A1 |
| G43 | P7, verheiratet seit 2028-05-01 (Dauer egal) | ja | 97'000 | fest |
| G44 | P7, Mutter des Kindes wohnt ausserhalb des Kantons | ja | 97'000; Anspruch ja, weil der Vater das Gesuch stellt und im Kanton wohnt | Entscheid O8 |

### Aktuelle Gegebenheiten (KiBG 5.4, KiBV 11)

Einkommen gemäss Steuerveranlagung 100'000 (Mutter allein, ausser G48).

| Nr. | Aktuelles Einkommen | Antrag | Abweichung | `kibg_massgebendes_einkommen` | Status |
|---|---|---|---|---|---|
| G45 | 75'000 | ja | −25 % | 75'000 | fest |
| G46 | 76'000 | ja | −24 % | 100'000 | fest |
| G47 | 70'000 | nein | −30 % | 100'000 | fest |
| G48 | Paar: Steuerveranlagung 60'000 + 40'000; aktuell 60'000 + 15'000 = 75'000 | ja | −25 % (Haushalt) | 75'000 | fest |

Höheres aktuelles Einkommen: siehe Q4.

### Mehrere Kinder und Perioden

| Nr. | Änderung | Erwartet | Status |
|---|---|---|---|
| G49 | P3, aber Mia geboren 2028-07-01 (2 Monate) | Mia: kein Anspruch, Beitrag 0.00, Restkosten 1'500.00; Leo unverändert 198.00 | A1 |
| G50 | P1 im Monat 2028-08 (erster Monat nach Vollzugsbeginn, Lina 11 Monate) | wie P1: 440.00 | fest |
| G51 | P4 im Monat 2029-01, Einkommen für 2029 gleich wie 2028 | wie P4: 375.00 (Elias 28 Monate, Ansatz unverändert) | A1 |

### Wohnsitz der gesuchstellenden Person (KiBG 4.1, Entscheid O8)

| Nr. | Änderung | `kibg_wohnsitz_erfuellt` | `kibg_anspruch` | Status |
|---|---|---|---|---|
| G52 | P1, der Vater wohnt ausserhalb des Kantons, die Mutter stellt das Gesuch | ja | ja, Beitrag 440.00 | Entscheid O8 |
| G53 | P1, der Vater wohnt ausserhalb des Kantons und stellt das Gesuch | nein | nein, Beitrag 0.00, Restkosten 1'040.00 | Entscheid O8 |

---

## Teil 3: Kein Anspruch

Ausgehend von P1. Erwartet ist jeweils `kibg_anspruch` = nein, alle Beiträge und Anteile 0.00 und `kibg_restkosten_eltern` = volle Kosten (1'040.00; bei X9 wie P7 864.00).

| Nr. | Änderung | Grund | Quelle | Status |
|---|---|---|---|---|
| X1 | Beide Eltern wohnen ausserhalb des Kantons | Wohnsitz | KiBG 4.1 | fest |
| X2 | Einrichtung nicht angemeldet | Einrichtung | KiBG 3.3 | fest |
| X3 | Einrichtung nicht anerkannt | Einrichtung | KiBG 3.2 | fest |
| X4 | Keine anerkannte Einrichtung (z. B. private Nanny), Typ `keine` | Einrichtung | KiBG 3.2 | fest |
| X5 | Kind geboren 2016-05-01 (12 Jahre), Primarschule abgeschlossen | Alter | KiBG 4.3 | fest |
| X6 | Paar, 100 % + 0 %, keine Ausnahme | Beschäftigung | KiBG 4.1 | fest |
| X7 | Paar, 100 % + 0 %, Ausnahmegrund erfasst (familiäre Belastung), Ausnahme aber nicht bewilligt | Der Entscheid der Gemeinde fehlt; der Grund allein genügt nicht | KiBG 4.2, KiBV 12 | fest |
| X8 | Paar, 100 % + 0 %, Ausnahme bewilligt, aber beide Eltern wohnen ausserhalb des Kantons | Die Ausnahme ersetzt nur das Pensum, nicht den Wohnsitz | KiBG 4.1–4.2 | fest |
| X9 | P7, aber der Vater (Gesuchsteller) wohnt ausserhalb des Kantons | Wohnsitz der gesuchstellenden Person | KiBG 4.1 | Entscheid O8 |
| X10 | Monat 2028-07 (vor Vollzugsbeginn) | Das Gesetz gilt noch nicht | KiBG IV, KiBV IV | Entscheid O1 |

### Teil 3b: Eingabefehler (keine Berechnung)

Ohne diese Angaben lässt sich der Text nicht anwenden. Der Rechner liefert dann **keinen Betrag**, sondern eine Fehlermeldung (über die Web-API als Fehler 400 mit Hinweis auf das fehlende Feld). Getestet in `openfisca-CH-SG/openfisca_ch_sg/tests/test_eingabefehler.py`.

| Nr. | Fall | Erwartet | Grund |
|---|---|---|---|
| F1 | P1, aber ohne Geburtsdatum von Lina | Fehler beim Feld `geburtsdatum` von Lina | Ohne Geburtsdatum lassen sich Mindestalter (KiBG 4.3) und Höchstbeitrag (KiBV 14) nicht bestimmen |
| F2 | P1, aber niemand ist als gesuchstellend angegeben | Fehler beim Feld `kibg_gesuchstellend` | Bei zwei Erziehungsberechtigten muss feststehen, wessen Wohnsitz zählt (KiBG 4.1, O8) |
| F3 | P1, beide Eltern als gesuchstellend angegeben | Fehler beim Feld `kibg_gesuchstellend` | Nur eine Person stellt das Gesuch |
| F4 | P1 mit Partnerin, die als gesuchstellend angegeben ist | Fehler beim Feld `kibg_gesuchstellend` der Partnerin | Das Gesuch stellen Erziehungsberechtigte (KiBG 9.1) |
| F5 | P1, aber «kein gemeinsamer Haushalt» (beide Eltern erfasst) | Fehler beim Feld `gemeinsamer_haushalt` | Bei getrennten Eltern ist nur die gesuchstellende Person erziehungsberechtigt (KiBG 2.1); sonst würde das Pensum der anderen Person zählen (KiBG 4.1a), ihr Einkommen aber nicht (KiBV 8.1b) |
| F6 | Mutter allein, aber «gemeinsamer Haushalt» | Fehler beim Feld `gemeinsamer_haushalt` | Ein gemeinsamer Haushalt der Erziehungsberechtigten (KiBV 8.1a) setzt zwei Erziehungsberechtigte voraus |
| F7 | P1, 80 Stunden, aber 0 Betreuungstage | Fehler beim Feld `betreuungstage_mit_obhut` | Die Stunden zählen höchstens je Betreuungstag (KiBV 14.4) |
| F8 | P1, Lina (12 Monate) als eingeschult angegeben | Fehler beim Feld `eingeschult` | Für Kinder unter 18 Monaten gilt KiBV 14.1; sie können nicht eingeschult sein |
| F9 | P1, aktuelles Einkommen der Mutter −5'000 | Fehler beim Feld `me_aktuell` | Negative Werte würden sonst still wie «nicht angegeben» behandelt |
| F10 | P1, aber ohne Betreuungsbeginn | Fehler beim Feld `betreuungsbeginn` | Ohne ihn lässt sich der Beitragsbeginn nicht bestimmen (KiBG 9.2) |
| F11 | P1, aber ohne Gesuchsdatum | Fehler beim Feld `kibg_gesuchsdatum` | Ohne es lässt sich der Beitragsbeginn nicht bestimmen (KiBG 9.2, KiBV 25) |
| F12 | P1, Kita am 2028-09-01 bestätigt, im September aber als angemeldet angegeben | Fehler beim Feld `kibg_einrichtung_angemeldet` | Nach KiBV 6 nimmt die Kita erst ab 2028-10-01 teil |
| F13 | Gesuch wird am 2028-11-15 abgegeben, im November 20 Betreuungstage | Fehler beim Feld `betreuungstage_mit_obhut` | Ab dem 15. November bleiben nur 16 Tage (A9); mit 16 Tagen ist es kein Fehler |
| F14 | Kita ab 2029-03-15 (Verfügung bis 2030-03-14), im März 2030 20 Betreuungstage | Fehler beim Feld `betreuungstage_mit_obhut` | Bis zum 14. März bleiben 14 Tage (A12) |
| F15 | Wie F14, aber 14 Betreuungstage | kein Fehler, Verfügung läuft im März 2030 | Grenze genau erreicht (A12) |

---

## Teil 4: Auslegungsfälle

Hier wären zwei Ergebnisse vertretbar. Das Team hat entschieden; die Fälle sind jetzt normale Tests und zugleich Material für die Stellungnahme.

| Nr. | Fall | Entscheid | Erwartet | Verworfene Lesart | Frage |
|---|---|---|---|---|---|
| Q1 | P1, Kind geboren 2027-03-01 (am 1. September 2028 genau 18 Monate) | Der tiefere Ansatz gilt ab dem 18-Monate-Geburtstag, also ab dem ersten Tag des 19. Lebensmonats; die vollen 18 Lebensmonate gilt der höhere | MaxV 7.50, Beitrag 300.00 | weiterhin 11.00 → 440.00 | O2 |
| Q2 | Paar, 120 % + 0 % | lit. a und b kumulativ: jeder Elternteil mindestens 20 % | Anspruch nein | nur die Summe zählt → Anspruch ja | O3 |
| Q3 | P1 mit Einkommen 160'000 und `kibg_zusatzbeitrag_z2` = 1.00 | Z2 ist einkommensunabhängig und gilt auch über 154'000; KiBV 15.2 betrifft nur den Mindestbeitrag | Mindestbeitrag 0.00, Zusatzbeitrag 80.00, Anteil Gemeinde 80.00, Restkosten 960.00 | kein Beitrag → 0.00 | O4 |
| Q4 | G45, aber aktuelles Einkommen 130'000 (+30 %), Antrag ja | Die Abweichung von 25 % zählt in beide Richtungen | `kibg_massgebendes_einkommen` 130'000 | nur Senkungen → 100'000 | O12 |

---

## Teil 5: Bekannte Einschränkungen

| Nr. | Fall | Rechner | Nach Gesetz | Status |
|---|---|---|---|---|
| E1 | P1, aber 6 Tage pro Woche: 26 Tage, 260 Stunden, Kosten 3'380 | subventioniert 260 Stunden → 1'430.00 | höchstens 5 von 6 Tagen: rund 21.7 Tage, 216.7 Stunden → 1'191.65 (gerundet) | A3 |
| E2 | Kind nutzt im selben Monat zwei Betreuungsformen (z. B. Tagesstruktur und Tagesfamilie) | nur ein Einrichtungstyp pro Kind und Monat; die Eltern müssen den Fall in zwei Rechnungen aufteilen | je Betreuungsform der eigene Ansatz | kein Test, nur Dokumentation |

E1 belegt die dokumentierte Grenze: Der Rechner liefert hier bewusst den zu hohen Wert. Wird die Grenze später umgesetzt, muss der Test angepasst werden.

---

## Teil 6: Datumsregeln (KiBG 9.2, KiBV 25 und 6)

Ab wann Beiträge fliessen. Grundlage ist P1 (Lina, Kita, 80 Stunden an 8 Tagen, Kosten 1'040, Einkommen 97'000, Faktor 0.5); geändert werden nur die Daten. Vollzugsbeginn 2028-08-01; die Übergangsfrist nach KiBV 25.1 läuft bis und mit 2028-11-01 (A7). Für Fälle im Jahr 2029 gilt das Einkommen auch für 2029. Getestet in `openfisca-CH-SG/openfisca_ch_sg/tests/datumsregeln.yaml`.

**Regeln**

1. Gesuch innert 30 Tagen seit Betreuungsbeginn (KiBG 9.2 Satz 1, A7: bis Betreuungsbeginn + 30 Tage) → Beiträge ab Betreuungsbeginn. Ein Gesuch vor dem Betreuungsbeginn ist immer rechtzeitig.
2. Sonst ab dem Gesuchsdatum (KiBG 9.2 Satz 2).
3. Gesuch bis 2028-11-01 (KiBV 25.1) → ab Vollzugsbeginn, aber nicht vor dem Betreuungsbeginn. Diese Regel geht 1 und 2 vor.
4. Vor dem Beitragsbeginn besteht kein Anspruch (Teamentscheid). Im Monat des Beitragsbeginns zählen nur die Stunden ab diesem Tag (A9).
5. Ist das Datum der Bestätigung der Kita bekannt, nimmt sie ab dem Ersten des Folgemonats teil (KiBV 6); das Datum hat Vorrang vor der Angabe «angemeldet».

**Beitragsbeginn (KiBG 9.2, KiBV 25)**

| Nr. | Betreuungsbeginn | Gesuch | `kibg_gesuch_innert_frist` | `kibg_gesuch_in_uebergangsfrist` | `kibg_beitragsbeginn` | Ergebnis pro Monat | Status |
|---|---|---|---|---|---|---|---|
| D1 | 2029-03-01 | 2029-03-31 (30 Tage später) | ja | nein | 2029-03-01 | März 2029: Anspruch ja, 300.00 (Lina 18 Monate, Ansatz 7.50) | A7 |
| D2 | 2029-03-01 | 2029-04-01 (31 Tage später) | nein | nein | 2029-04-01 | März 2029: kein Anspruch, 0.00, Restkosten 1'040.00; April 2029: 300.00 | A7 |
| D3 | 2028-08-01 | 2028-10-15 | nein | ja | 2028-08-01 | August 2028: 440.00 | fest |
| D4 | 2028-08-01 | 2028-11-15 | nein | nein | 2028-11-15 | Oktober 2028: kein Anspruch, 0.00, Restkosten 1'040.00; November 2028 mit 4 Tagen, 40 Stunden ab dem 15., Kosten 520: 220.00, Restkosten 300.00 | A9 |
| D5 | 2028-09-15 | 2028-10-31 (46 Tage später) | nein | ja | 2028-09-15 (nicht vor dem Betreuungsbeginn) | September 2028 mit 4 Tagen, 40 Stunden, Kosten 520: 220.00 | A9 |
| D6 | 2026-01-01 | 2028-09-10 | nein | ja | 2028-08-01 (höchstens bis Vollzugsbeginn) | August 2028: 440.00 | fest |
| D7 | 2028-08-01 | 2028-11-01 (letzter Tag der Übergangsfrist) | nein | ja | 2028-08-01 | August 2028: Anspruch ja | A7 |
| D10 | 2029-03-01 | 2029-02-10 (vor dem Betreuungsbeginn) | ja | nein | 2029-03-01 | Februar 2029: kein Anspruch, 0.00; März 2029: 300.00 | fest |

**Teilnahme der Einrichtung (KiBV 6)**

Bei diesen Fällen ist «angemeldet» mit nein angegeben; massgebend ist das Datum der Bestätigung.

| Nr. | Gesuch | Kita bestätigt am | `kibg_einrichtung_teilnahmebeginn` | Ergebnis pro Monat | Status |
|---|---|---|---|---|---|
| D8 | 2028-08-15 | 2028-08-20 | 2028-09-01 | August 2028: Einrichtung nicht berechtigt, kein Anspruch, 0.00; September 2028: 440.00 | fest |
| D9 | 2028-08-15 | 2028-09-01 | 2028-10-01 | September 2028: Einrichtung nicht berechtigt, 0.00 | fest |
| D11 | 2028-08-20 (Übergangsfrist, Beitragsbeginn 2028-08-01) | 2028-08-10 | 2028-09-01 | August 2028: kein Anspruch, 0.00, Restkosten 1'040.00, obwohl der Beitragsbeginn erreicht ist; September 2028: 440.00 | fest |

D1, D2 und D10 liegen bewusst im Jahr 2029, ausserhalb der Übergangsfrist, damit nur KiBG 9.2 wirkt.

### Dauer der Verfügung (KiBG 11.2, KiBV 16 und 25.2)

Familie P1 wie D1; geändert werden nur die Daten. Schuljahresbeginn 1. August (O9). Die Verfügung beginnt mit dem Beitragsbeginn (A11). Getestet in `datumsregeln.yaml`.

| Nr. | Fall | Monat | `kibg_verfuegung_ende` | Erwartet | Quelle | Status |
|---|---|---|---|---|---|---|
| D12 | Kita, Beitragsbeginn 2028-08-01 | 2029-07 | 2029-07-31 | Verfügung läuft, Beitrag 300.00 (Lina 22 Monate) | KiBG 11.2, KiBV 16.1 | A11 |
| D13 | wie D12 | 2029-08 | 2029-07-31 | Verfügung abgelaufen: kein Anspruch, Restkosten 1'040.00 | KiBV 16.1, 16.4 | A11 |
| D14 | Kita, Beitragsbeginn 2029-03-15 | 2030-03 | 2030-03-14 | Verfügung läuft noch (8 Tage bis zum 14. März) | KiBV 16.1 | A11, A12 |
| D15 | Schulkind, schulergänzende Betreuung ab 2028-08-01 | 2028-09 | 2029-07-31 | ein Schuljahr | KiBV 16.2 Satz 1 | A11 |
| D16 | Schulkind ab 2029-01-08 | 2029-01 | 2029-07-31 | bis Ende des laufenden Schuljahres | KiBV 16.2 Satz 2 | A11 |
| D17 | Kita, Kindergarteneintritt 2029, Beitragsbeginn 2029-02-01 | 2029-02 | 2029-07-31 | im Jahr der Schulpflicht nur bis Schuljahresbeginn | KiBV 16.1 Satz 2 | A8, A11 |
| D18 | wie D17, Jahr nicht angegeben | 2029-02 | 2030-01-31 | nur die zwölf Monate | KiBV 16.1 Satz 1 | A11 |
| D19 | wie D17, Beitragsbeginn 2029-09-01 (nach Schuljahresbeginn) | 2029-09 | 2030-07-31 | gilt als Schulkind: ein Schuljahr, nicht zwölf Monate | KiBV 16.2, A8 | A11 |

---

## Teil 7: Unklare Stellen im Text

Hier ist das Recht nicht genau genug: Der Wortlaut lässt zwei oder mehr Lesarten zu, schweigt zu einem Fall, oder Gesetz und Verordnung passen nicht zusammen. Für jede Stelle steht, was unklar ist, ein konkretes Beispiel, was die Lesarten bewirken (in Franken, wenn möglich), wie das Modell heute damit umgeht und ob das Team schon entschieden hat.

Die Beispiele gehen von P1 aus (Faktor 0.5, Kita, 80 Stunden), wenn nichts anderes steht. Die Beträge sind wie im übrigen Katalog gerechnet.

**Stand**

- **entschieden:** Das Team hat eine Auslegung gewählt (O… oder A…); sie ist im Modell umgesetzt.
- **offen:** Noch kein Entscheid; das Modell folgt einer Lesart oder lässt die Frage über die Eingabe offen.
- **Stellungnahme:** eignet sich für die Stellungnahme zur Verordnung (Vernehmlassung bis 15. November 2026). Bei Stellen im Gesetz eignet sie sich als Hinweis an den Kanton.

### 7.1 Bereits entschieden

| Stelle | Was unklar war | Entscheid |
|---|---|---|
| KiBV 14.1–14.2 | Kind mit genau 18 Monaten: weder «unter» noch «über» 18 Monaten | O2: tieferer Ansatz ab dem 18-Monate-Geburtstag (Q1) |
| KiBG 4.1 lit. a und b | Genügt bei Paaren die Summe von 120 %? | O3: kumulativ, jede Person mindestens 20 % (Q2) |
| KiBV 15.2, Anhang | Gilt «kein Beitrag» über Fr. 154'000 auch für Z2? | O4: Z2 wird auch darüber ausgerichtet (Q3) |
| KiBG 4.1, KiBV 2 | Welcher Elternteil muss im Kanton wohnen? | O8: die gesuchstellende Person (G52, G53) |
| KiBV 7, 8.1b | Alternierende Obhut: wer stellt das Gesuch? | O10: jeder Elternteil für die eigenen Tage |
| KiBV 11.2 | Zählt die Abweichung von 25 % auch nach oben? | O12: in beide Richtungen (Q4) |
| KiBG 3.2d, KiBV 14.3 | Ansatz für private Sonderschulen | O11 erledigt: Betrag nach Betreuungsform |
| Ganzer Text | Stichtag für Alter und Dauer des Konkubinats im Monat | A1: erster Tag des Monats |
| Ganzer Text | Rundung | A4: kaufmännisch auf 5 Rappen |
| KiBG 9.2, KiBV 25 | Berechnung der Fristen | A7: sinngemäss Art. 77 OR |
| KiBV 14.2–14.3, 16.1 | Ab wann ist ein Kind «eingeschult»? | A8: ab Kindergarten |
| KiBG 9.2 | Beitragsbeginn mitten im Monat | A9: nur Stunden ab dem Stichtag |
| KiBG 9.2 | Zählt der Eingang oder die Abgabe des Gesuchs? | A10: die Abgabe, auch per Post (U19) |
| KiBV 14.4 | Höchstens 5 Tage pro Woche bei Monatswerten | A3: nicht geprüft (E1) |

### 7.2 Neu gefundene unklare Stellen

#### Einrichtungen

| Nr. | Bestimmung | Was unklar ist | Beispiel und Folge | Umgang im Modell | Stand |
|---|---|---|---|---|---|
| U1 | KiBG 3.2c | «Einrichtungen für schulergänzende Betreuung des Volksschulträgers sowie … beauftragte private Trägerschaften, die über ein Qualitätskonzept … verfügen»: Bezieht sich das Qualitätskonzept nur auf die privaten Trägerschaften oder auch auf die Einrichtungen des Volksschulträgers? KiBV 4.2 befreit öffentliche Einrichtungen nur vom **Nachweis**, nicht von der Voraussetzung | Eine Tagesstruktur der Schulgemeinde ohne Qualitätskonzept: nach Lesart 1 anerkannt, nach Lesart 2 nicht; im zweiten Fall Fr. 0 statt Beitrag | Eingabe `kibg_einrichtung_anerkannt`; die Frage stellt sich nicht | offen |
| U2 | KiBV 3, KiBG 3.2c–d, 23f | KiBV 3 lässt auch **ausserkantonale** Einrichtungen zu. Für schulergänzende Betreuung verlangt KiBG 3.2c–d aber ein Qualitätskonzept bzw. eine Leistungsvereinbarung nach dem **St. Galler** Volksschulgesetz, das ausserkantonale Angebote nicht erfüllen können. KiBG 23f verlangt Regeln zum Verfahren bei ausserkantonaler Betreuung, die KiBV enthält keine | Kind wohnt in Wil SG, besucht den Mittagstisch in Sirnach TG: Kita in Sirnach wäre anerkannt (Bundesrecht), der Mittagstisch kaum | Eingabe `kibg_einrichtung_anerkannt` | offen, Stellungnahme |
| U3 | KiBV 5.3, 6 | Das Amt kann die Teilnahme **provisorisch** bestätigen. Art. 6 sagt nicht, ob der Teilnahmebeginn an die provisorische oder an die definitive Bestätigung anknüpft, und nicht, was gilt, wenn die Nachweise nicht innert eines Monats nachgereicht werden | Provisorisch bestätigt 20.8., definitiv 25.9.: Teilnahme ab 1.9. oder erst ab 1.10.? Im September Fr. 440 oder Fr. 0 | Eingabe `kibg_einrichtung_bestaetigt_am`: es zählt das eingegebene Datum | offen, Stellungnahme |
| U4 | KiBG 3.3, KiBV 5–6 | Nach dem Gesetz ist eine Einrichtung «angemeldet», sobald sie sich angemeldet hat. Nach der Verordnung nimmt sie erst ab dem Folgemonat nach der **Bestätigung** teil. Zwischen Anmeldung und Bestätigung ist sie angemeldet, nimmt aber nicht teil; die Verordnung ist strenger als das Gesetz | Anmeldung 1.8., Bestätigung 10.9.: nach dem Gesetz Beiträge ab August möglich, nach der KiBV erst ab Oktober | Folgt der KiBV (Art. 6, Datum hat Vorrang) | offen, Stellungnahme |
| U5 | KiBG 3.2b | «Tagesfamilienorganisationen, deren angeschlossene Tagesfamilien … gemeldet sind»: Müssen **alle** angeschlossenen Tagesfamilien gemeldet sein oder nur jene, die das Kind betreut? | Eine Organisation mit einer nicht gemeldeten Familie: Ist die ganze Organisation nicht anerkannt? | Eingabe `kibg_einrichtung_anerkannt` | offen |

#### Wer anspruchsberechtigt ist

| Nr. | Bestimmung | Was unklar ist | Beispiel und Folge | Umgang im Modell | Stand |
|---|---|---|---|---|---|
| U6 | KiBG 2.1, 4.1b, KiBV 8.1a | Erziehungsberechtigte sind nach Art. 2.1 «Personen, die … Beiträge … geltend machen». Bei einem Paar stellt aber nur eine Person das Gesuch. Ist die andere dann erziehungsberechtigt im Sinn des Gesetzes? Davon hängen lit. b (zusammen 120 %) und das gemeinsame Einkommen (KiBV 8.1a) ab | P1: Ist nur die Mutter erziehungsberechtigt, zählt nur ihr Einkommen (60'000 statt 97'000) und lit. b entfällt | Beide Eltern im gemeinsamen Haushalt gelten als erziehungsberechtigt (Teamentscheid, F5, F6) | entschieden im Modell, Wortlaut unklar |
| U7 | KiBV 8.1a–b | Beide Buchstaben setzen **zwei** Erziehungsberechtigte voraus («gemeinsamer» bzw. «getrennter Haushalt der Erziehungsberechtigten»). Für eine alleinerziehende Person ohne zweiten Elternteil (verstorben, unbekannt) passt keiner. Zählt das Einkommen eines Partners in gefestigter Lebensgemeinschaft dann mit? | Wie P7, aber ohne anderen Elternteil: Partnerin zählt → Fr. 270; zählt nicht → Fr. 486 | Wie lit. b: Partnerin zählt mit | offen, Stellungnahme |
| U8 | KiBG 4.1 | Wie wird der Beschäftigungsgrad bei **Selbständigen** (kein Arbeitsvertrag) und bei **schwankenden Pensen** (Stundenlohn, Saison) bestimmt, und über welchen Zeitraum? | Selbständige Grafikerin mit 10–30 % je nach Monat: erfüllt sie lit. a? | Eingabe `beschaeftigungsgrad` pro Monat | offen, Stellungnahme |
| U9 | KiBG 4.1–4.2, KiBV 12a | Art. 4.2 entbindet nur vom «minimalen **Beschäftigungsgrad**». Art. 4.1 verlangt aber zusätzlich, dass eine Erwerbstätigkeit **ausgeübt** wird. KiBV 12a nennt Stellensuche und Ausbildung, also Fälle ohne Erwerbstätigkeit. Geht die Verordnung über das Gesetz hinaus? | Mutter in Ausbildung, 0 %: nach der KiBV Ausnahme möglich (G37: Fr. 594), nach dem Wortlaut des Gesetzes nicht | Die Ausnahme ersetzt die ganze Bedingung zum Beschäftigungsgrad | offen, Stellungnahme |
| U10 | KiBG 4.2 | Entbindet die Ausnahme eine **Person** (nur lit. a) oder den **Haushalt** (auch lit. b)? | Vater 100 %, Mutter 0 % mit Ausnahme: gilt lit. b (zusammen 120 %) weiter, gibt es keinen Anspruch | Gilt für den Haushalt: Anspruch ja (G36) | offen |

#### Einkommen

| Nr. | Bestimmung | Was unklar ist | Beispiel und Folge | Umgang im Modell | Stand |
|---|---|---|---|---|---|
| U11 | KiBG 5.4, KiBV 11.1 | Das Gesetz ist **zwingend**: Hat sich das Einkommen wesentlich verändert, «werden» die aktuellen Gegebenheiten massgebend. Die Verordnung macht daraus eine Bemessung **nur auf Antrag**. Bei höherem Einkommen stellt kaum jemand einen Antrag | Veranlagt 60'000, aktuell 100'000 (+67 %), kein Antrag: nach der KiBV Fr. 725.60, nach dem Gesetz Fr. 416.85 pro Monat (Differenz Fr. 308.75) | Folgt der KiBV: nur auf Antrag (G47) | offen, Stellungnahme |
| U12 | KiBG 5.3 | «**in der Regel** die letzte definitive Steuerveranlagung»: Welche Ausnahmen gibt es ausser Abs. 4? Die letzte definitive Veranlagung kann zwei bis drei Jahre alt sein | Gesuch 2028, letzte definitive Veranlagung 2025 | Eingabe des Einkommens | offen |

#### Höhe des Beitrags

| Nr. | Bestimmung | Was unklar ist | Beispiel und Folge | Umgang im Modell | Stand |
|---|---|---|---|---|---|
| U13 | KiBG 6.2, 20.3 | «Kosten … für das in Anspruch genommene Betreuungsangebot»: Gehören **Mahlzeiten**, Material oder Anmeldegebühren dazu? Und gilt die Obergrenze pro Monat, pro Rechnung oder für die ganze Verfügung? | Faktor 1, 100 Stunden, Rechnung 1'200 inkl. 200 für Mahlzeiten: mit Mahlzeiten Fr. 1'100, ohne Fr. 1'000 | Kosten werden eingegeben; pro Monat | offen, Stellungnahme |
| U14 | KiBV 14, 17.1, Anhang | Was ist eine **Betreuungsstunde**: die gebuchte oder die tatsächlich besuchte? Nach KiBV 17.1 erfasst die Einrichtung den «Betreuungsumfang», ohne zu sagen, welchen. Für Module und Monatspauschalen fehlen die Richtlinien (O7) | 80 Stunden gebucht, 2 Tage krank (60 Stunden besucht): Fr. 440 oder Fr. 330 | Eingabe `betreuungsstunden` | offen, Stellungnahme |
| U15 | KiBG 11.2–11.3, KiBV 16.3 | Ändert sich der Beitrag **während** einer Verfügung, wenn das Kind 18 Monate alt wird? KiBV 16.3 regelt nur Senkungen wegen Modelländerungen, nicht wegen des Alters | Lina wird mitten in der Verfügung 18 Monate: sofort Fr. 300 statt Fr. 440, oder bis zum Ende der Verfügung weiter Fr. 440 (bis zu Fr. 140 pro Monat) | Monatlich: der Beitrag sinkt ab dem 18-Monate-Geburtstag | offen, Stellungnahme |
| U16 | KiBG 18.1, KiBV 2 | **Umzug** in eine andere Gemeinde während einer Verfügung: Welche Gemeinde trägt den Anteil, und wessen Zusatzbeiträge gelten im Monat des Umzugs? | Umzug am 15. von St. Gallen nach Gossau mit anderen Z1/Z2 | Eine Gemeinde pro Monat (`wohngemeinde`), Z1/Z2 als Eingabe | offen |

#### Verfahren und Fristen

| Nr. | Bestimmung | Was unklar ist | Beispiel und Folge | Umgang im Modell | Stand |
|---|---|---|---|---|---|
| U17 | KiBG 9.2, KiBV 16.4 | «Datum der **Inanspruchnahme** des Betreuungsangebots»: der erste Tag der Betreuung überhaupt, der erste Tag in **dieser** Einrichtung oder der Beginn der neuen Verfügungsperiode bei einem **Folgegesuch**? | Verfügung endet 31.7.2029, Folgegesuch trifft am 15.9.2029 ein. Zählt die Frist ab dem ersten Betreuungsbeginn 2028, gibt es erst ab 15.9. Beiträge: August Fr. 300 und halber September Fr. 150 verloren | Betreuungsbeginn wird eingegeben; die Frage entscheidet, wer ihn eingibt | offen, Stellungnahme |
| U18 | KiBV 16.1–16.2 | Ein **eingeschultes Kind in einer Kita** oder Tagesfamilie: Gilt die Verfügung 12 Monate (Abs. 1: Kita und Tagesfamilie) oder ein Schuljahr (Abs. 2: eingeschulte Kinder)? | Verfügung im Oktober: bis September des Folgejahres oder bis Ende Juli? | Dauer der Verfügung nicht umgesetzt (README) | offen, Stellungnahme |
| U19 | KiBG 9.2 | «eingereicht»: Zählt der **Eingang** bei der Gemeinde oder schon die **Postaufgabe**? | Gesuch am Tag 30 aufgegeben, am Tag 31 eingetroffen: rückwirkend oder nicht | A10: Die Abgabe zählt, auch die Postaufgabe; das Gesuch im Beispiel ist rechtzeitig | entschieden (Rechtsteam) |
| U20 | KiBV 25.1 | Gilt die Übergangsfrist auch für Gesuche **vor** dem Vollzugsbeginn, und gibt es die Plattform dann schon? | Gesuch im Juli 2028 für eine Betreuung ab August | Ja, auch frühere Gesuche zählen (beim Umsetzen festgelegt und im Commit dokumentiert; vom Team zu bestätigen) | offen |

#### Redaktionelles und Unvollständiges

| Nr. | Bestimmung | Was unklar ist | Folge | Umgang im Modell | Stand |
|---|---|---|---|---|---|
| U21 | KiBG 18.1, 20.1 | Art. 18.1 spricht von «Beiträgen nach Art. 6 **und 17**», Art. 20.1 von «Beiträgen nach Art. 6, **17 und 18**». Art. 17 und 18 regeln aber das Budget und die Finanzierung, keine Beiträge | Keine Folge für den Betrag; unklare Verweise | Mindestbeitrag = Beitrag nach Art. 6 | Hinweis an den Kanton |
| U22 | KiBV 21.1a Ziff. 13, 21.1b Ziff. 5 | «[Daten werden im Rahmen der Konzeptphase von IT-KiBG weiter spezifiziert]»: Die Liste der bearbeiteten Daten ist offen. Art. 8 KiBG verlangt eine klare Grundlage für die Bearbeitung besonders schützenswerter Daten | Wichtig für den Teil zu Datenschutz und Ethik | Der Rechner fragt nur das Nötige ab (Datenminimierung) | Stellungnahme |
| U23 | Gesetz (Titelseite) | Unser Gesetzestext ist die Fassung der **ersten Lesung** (16. September 2025); die KiBV verweist auf das Gesetz vom 14. Juni 2026 (O6) | Weicht der Schlusstext ab, können Artikel oder Werte nicht stimmen | Fassung der ersten Lesung | offen, Organisatoren |
| U24 | KiBV 14.5 | Betreuungsmodule und Monatspauschalen regelt das Amt «mittels Richtlinien»; diese liegen nicht vor (O7) | Pauschal abgerechnete Angebote lassen sich nicht in Stunden umrechnen | Stunden werden eingegeben | offen |

### 7.3 Für die Stellungnahme besonders geeignet

Diese Stellen haben die grösste Wirkung auf Familien und lassen sich mit einem Satz in der Verordnung klären:

1. **U11:** KiBV 11.1 an KiBG 5.4 anpassen. Entweder wirkt die Bemessung nach aktuellen Gegebenheiten auch ohne Antrag, oder das Gesetz sagt klar, dass ein Antrag nötig ist.
2. **U15:** Festlegen, ob der Wechsel des Ansatzes mit 18 Monaten während einer Verfügung wirkt.
3. **U17:** Festlegen, welche «Inanspruchnahme» bei Folgegesuchen und beim Wechsel der Einrichtung zählt.
4. **U13 und U14:** Festlegen, welche Kosten zählen und ob gebuchte oder besuchte Stunden.
5. **U2:** Das Verfahren für ausserkantonale Einrichtungen regeln, wie es KiBG 23f verlangt.
6. **U7:** Alleinerziehende ohne zweiten Elternteil in KiBV 8.1 ausdrücklich erfassen.
7. **U9:** Klarstellen, dass die Ausnahme auch vom Erfordernis der Erwerbstätigkeit entbindet, oder KiBV 12a enger fassen.

---

## Anhang: P1 als OpenFisca-Test

So wird ein Szenario zum Test. Bei zwei Erziehungsberechtigten ist `kibg_gesuchstellend` Pflicht, für jedes Kind `betreuungsbeginn` und `kibg_gesuchsdatum` (Abgabedatum, A10). Dieselben Angaben stehen als echter Test in `openfisca-CH-SG/openfisca_ch_sg/tests/personas.yaml`.

```yaml
- name: P1 Paar, ein Kleinkind in der Kita
  period: 2028-09
  absolute_error_margin: 0.01
  input:
    household:
      erziehungsberechtigte: [mutter, vater]
      kinder: [lina]
      gemeinsamer_haushalt: true
    persons:
      mutter:
        wohnsitz_kanton_sg: true
        beschaeftigungsgrad: 1.0
        kibg_gesuchstellend: true
        me_steuerveranlagung:
          2028: 60000
      vater:
        wohnsitz_kanton_sg: true
        beschaeftigungsgrad: 0.4
        me_steuerveranlagung:
          2028: 37000
      lina:
        geburtsdatum: 2027-09-01
        betreuungsbeginn: 2028-08-01
        kibg_gesuchsdatum: 2028-08-15
        kibg_einrichtungstyp: kita
        kibg_einrichtung_anerkannt: true
        kibg_einrichtung_angemeldet: true
        betreuungsstunden: 80
        betreuungstage_mit_obhut: 8
        kibg_betreuungskosten: 1040
  output:
    # Werte je Person in der Reihenfolge mutter, vater, lina
    kibg_beitrag_pro_stunde: [0, 0, 5.50]
    kibg_beitrag_total: [0, 0, 440]
    kibg_restkosten_eltern: [0, 0, 600]
    kibg_anteil_kanton: [0, 0, 220]
    kibg_anteil_gemeinde: [0, 0, 220]
```

---

## Abdeckung

Welche Bestimmung durch welche Fälle geprüft wird.

| Bestimmung | Inhalt | Fälle |
|---|---|---|
| KiBG 3.1–3.3 | Anerkannte und angemeldete Einrichtung | X2–X4, D8–D9 |
| KiBG 4.1 | Wohnsitz der gesuchstellenden Person | X1, X8–X9, G44, G52–G53, F2–F4 |
| KiBG 4.1a–b | Beschäftigungsgrad (lit. a und b getrennt geprüft) | P1–P7, G30–G35, G38, X6, Q2 |
| KiBG 4.2, KiBV 12 | Ausnahme | G36–G37, X7–X8 |
| KiBG 4.3 | Mindestalter, Ende Primarschule; Geburtsdatum Pflicht | G15–G17, G49, X5, F1 |
| KiBG 5.4, KiBV 11 | Aktuelle Gegebenheiten | G45–G48, Q4 |
| KiBG 6.2 | Kostenobergrenze | P6, G21–G24, G28 |
| KiBG 9.1–9.2, KiBV 25 | Gesuch, Rückwirkung, Übergang | D1–D7, D10–D11, F10–F11, F13 |
| KiBG 12.2 | Restkosten der Eltern | alle P, G18–G29 |
| KiBG 18.1 | Aufteilung Kanton / Gemeinde | alle P, G21–G29 |
| KiBG 20, KiBV 24 | Zusatzbeiträge Z1, Z2 | P5, P6b, G24, G29, G39, Q3 |
| KiBV 6 | Teilnahmebeginn der Einrichtung | D8–D9, D11, F12 |
| KiBV 7 | Nur Tage mit Obhut | P7 (A5) |
| KiBV 8 | Einkommen im Haushalt | P1, P3, P7, P7b, G40–G43, G48 |
| KiBV 14.1–14.3 | Höchstbeitrag nach Alter und Betreuungsform | P1–P4, G7–G14, Q1 |
| KiBV 14.4 | Höchstens 12 Stunden pro Tag, 5 Tage pro Woche | G18–G20, E1 |
| KiBV 15, Anhang | Einkommensfaktor und Formel | alle P, G1–G6 |
| Vollzugsbeginn | Geltung ab 2028-08-01 | G50, X10 |
| A4 | Rundung | G25–G29 |

Nicht abgedeckt, weil nicht modelliert: Rückerstattung (KiBG 13, R1 im Inventar), Dauer der Verfügung (KiBV 16), Budgetsteuerung (KiBG 17).

---

## Kontrolle

Jede Rechnung soll eine zweite Person nachrechnen, bevor sie zum Test wird.

| Teil | Nachgerechnet von | Datum |
|---|---|---|
| Teil 1 (P1–P7b) | | |
| Teil 2 (G1–G53) | | |
| Teil 3 (X1–X10, F1–F13) | | |
| Teil 4 (Q1–Q4) | | |
| Teil 5–6 (E1–E2, D1–D11) | | |
| Teil 7 (Beispiele U1–U24) | | |
