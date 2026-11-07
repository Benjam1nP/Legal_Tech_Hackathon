# Szenarien KiBG / KiBV (Eingaben und erwartete Ergebnisse)

Dieser Katalog beschreibt konkrete Familien und Grenzfälle mit den Beträgen, die der Rechner liefern muss. Die erwarteten Ergebnisse sind **von Hand aus dem Gesetz gerechnet**, nicht aus dem Code. So prüfen die Tests, ob der Code das Gesetz richtig umsetzt.

Verwendung:

- **Tests:** Jedes Szenario wird ein OpenFisca-Test (Beispiel im Anhang).
- **Frontend und Pitch:** Die Personas (Teil 1) sind die Beispielfamilien für die Demo.
- **Stellungnahme zur Verordnung:** Die Auslegungsfälle (Teil 4) zeigen an konkreten Zahlen, wo der Text unklar ist und wie wir ihn auslegen.

Die Variablennamen stammen aus `line-to-line-rules.md`, Abschnitt «Variablen: Entität und Periode».

**Status je Szenario**

- **fest:** folgt eindeutig aus dem Text.
- **Annahme A…:** hängt von einer Annahme ab, die das Team getroffen hat, weil der Text schweigt (siehe unten).
- **Entscheid O…:** hängt von einer Auslegungsfrage ab, die das Team entschieden hat (siehe `line-to-line-rules.md`, offene Fragen).

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

**Rechenweg pro Kind und Monat**

1. Anspruch prüfen (KiBG 3–4). Kein Anspruch → alle Beträge 0.
2. Subventionierte Stunden = min(Betreuungsstunden, Betreuungstage × 12) (KiBV 14.4).
3. Mindestbeitrag = min(MaxV × F × subventionierte Stunden, Kosten) (KiBG 6.2).
4. Zusatzbeitrag = (Z1 × F + Z2) × subventionierte Stunden, gekürzt, sodass Mindest- + Zusatzbeitrag die Kosten nicht übersteigen (KiBG 20.3).
5. Beitrag total = Mindestbeitrag + Zusatzbeitrag. Mindest- und Zusatzbeitrag werden je auf 5 Rappen gerundet (A4).
6. Restkosten der Eltern = Kosten − Beitrag total (KiBG 12.2).
7. Anteil Kanton = Mindestbeitrag / 2, auf 5 Rappen gerundet; Anteil Gemeinde = Mindestbeitrag − Anteil Kanton + Zusatzbeitrag (KiBG 18.1, 20.2).

### Standardwerte

Wenn bei einem Szenario nichts anderes steht, gilt:

- Monat: **2028-09** (Vollzugsbeginn als Platzhalter: 1. August 2028)
- Alle Erwachsenen haben Wohnsitz im Kanton St. Gallen.
- Einrichtung anerkannt und angemeldet; Kind nicht eingeschult, Primarschule nicht abgeschlossen.
- Keine Zusatzbeiträge der Gemeinde (`kibg_zusatzbeitrag_z1` = `kibg_zusatzbeitrag_z2` = 0); keine Ausnahme nach KiBG 4.2; kein Antrag auf aktuelle Gegebenheiten.
- Massgebendes Einkommen als Eingabe für das Jahr 2028.

### Annahmen (vom Team bestätigt)

| Nr. | Annahme | Grund | Betrifft |
|---|---|---|---|
| A1 | Alter des Kindes und Dauer einer Lebensgemeinschaft werden am **ersten Tag des Monats** bestimmt und gelten für den ganzen Monat | Der Beitrag wird pro Monat berechnet; der Text sagt nichts zum Stichtag | G7–G8, G14–G15, G26–G27 |
| A2 | Übersteigen Mindest- und Zusatzbeitrag die Kosten, wird **zuerst der Zusatzbeitrag** gekürzt | KiBG 6.2 begrenzt schon den Mindestbeitrag auf die Kosten; KiBG 20.3 begrenzt dann die Summe | P6b |
| A3 | Die Grenze von 5 Tagen pro Woche wird nicht geprüft (Teamentscheid, siehe Dokumentation) | Eingaben sind Monatswerte | E1 |
| A4 | Beträge in Franken werden **kaufmännisch auf 5 Rappen gerundet** (ab 2.5 Rappen auf, sonst ab). Gerundet werden die Monatsbeträge (Mindest- und Zusatzbeitrag, Anteil Kanton), nicht der Beitrag pro Stunde. Die Kostenobergrenze gilt nach dem Runden. Der Anteil der Gemeinde ist der Rest, damit die Summe stimmt. Die Restkosten der Eltern sind Kosten minus Beitrag, ohne weitere Rundung | Der Text regelt keine Rundung; 5 Rappen ist die kleinste Münze | G33–G35 |
| A5 | Die eingegebenen Stunden und Tage sind nur solche mit faktischer Obhut (KiBV 7) | Vereinfachung der Eingabe | alle |
| A6 | Beschäftigungsgrad: Jeder Elternteil braucht mindestens 20 % (KiBG 4.1a); Eltern im gemeinsamen Haushalt zusätzlich zusammen mindestens 120 % (KiBG 4.1b) | Entscheid zu O3: lit. a und b gelten kumulativ | G20–G25, G32, X6, Q2 |

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

- Anspruch: 100 % + 40 % = 140 % ≥ 120 % ✓; Kind älter als 3 Monate ✓
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

- Anspruch: 140 % ✓
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

Quelle: KiBV 14.1a, 14.3b. **Status: fest.** Zeigt: zwei Kinder, zwei Ansätze, gleicher Faktor.

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

Eingaben wie P1, zusätzlich **Z1 = 2.00** und **Z2 = 1.00** pro Stunde.

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
| Haushalt | Vater (erziehungsberechtigt) und Partnerin (nicht erziehungsberechtigt); kein gemeinsamer Haushalt mit der Mutter |
| Vater | Pensum 80 %, Einkommen 51'400 |
| Partnerin | Pensum 100 %, Einkommen 45'600; gemeinsamer Haushalt seit 2026-01-01, nicht verheiratet |
| Kind Jonas | geboren 2024-09-01 (4 Jahre), Kita, 8 Tage, 72 Stunden, Kosten 864 (72 × 12.00) |

**Rechnung**

- Anspruch: Vater 80 % ≥ 20 % ✓
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

**Status: fest.**

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

Alle Grenzfälle gehen von **P1** aus; angegeben ist nur, was sich ändert.

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

### Altersstufe und Einrichtungstyp (KiBV 14)

| Nr. | Änderung | MaxV | `kibg_beitrag_pro_stunde` | `kibg_mindestbeitrag` | Status |
|---|---|---|---|---|---|
| G7 | geboren 2027-03-02 (noch keine 18 Monate) | 11.00 | 5.50 | 440.00 | A1 |
| G8 | geboren 2027-02-28 (über 18 Monate) | 7.50 | 3.75 | 300.00 | A1 |
| G9 | Tagesfamilie, 12 Monate | 8.30 | 4.15 | 332.00 | fest |
| G10 | Tagesfamilie, geboren 2026-03-01 (30 Monate) | 5.50 | 2.75 | 220.00 | fest |
| G11 | Kita, eingeschult (geboren 2022-05-01) | 7.50 | 3.75 | 300.00 | fest |
| G12 | schulergänzende Betreuung, eingeschult (wie G11) | 5.50 | 2.75 | 220.00 | fest |
| G13 | Tagesfamilie, eingeschult (wie G11) | 5.50 | 2.75 | 220.00 | fest |

Genau 18 Monate (geboren 2027-03-01): siehe Q1, Ergebnis 7.50.

### Mindestalter (KiBG 4.3)

| Nr. | Änderung | `kibg_anspruch` | `kibg_beitrag_total` | Status |
|---|---|---|---|---|
| G14 | geboren 2028-06-01 (genau 3 Monate) | ja | 440.00 | A1 |
| G15 | geboren 2028-06-02 (noch keine 3 Monate) | nein | 0.00 | A1 |

### Stundenobergrenze (KiBV 14.4)

| Nr. | Änderung | `kibg_subventionierte_stunden` | `kibg_mindestbeitrag` | `kibg_restkosten_eltern` | Status |
|---|---|---|---|---|---|
| G16 | 10 Tage, 120 Stunden, Kosten 1'560 | 120 | 660.00 | 900.00 | fest |
| G17 | 10 Tage, 130 Stunden, Kosten 1'690 | 120 (nicht 130) | 660.00 | 1'030.00 | fest |

### Kostenobergrenze (KiBG 6.2)

| Nr. | Änderung | `kibg_mindestbeitrag` | `kibg_restkosten_eltern` | Kanton / Gemeinde | Status |
|---|---|---|---|---|---|
| G18 | Kosten genau 440 | 440.00 | 0.00 | 220 / 220 | fest |
| G19 | Kosten 400 | 400.00 | 0.00 | 200 / 200 | fest |

### Rundung auf 5 Rappen (A4)

Wie P1 (Kita, unter 18 Monaten, 80 Stunden, Kosten 1'040), das ganze Einkommen bei der Mutter.

| Nr. | Einkommen | ungerundet | `kibg_mindestbeitrag` | `kibg_anteil_kanton` / `kibg_anteil_gemeinde` | `kibg_restkosten_eltern` | Status |
|---|---|---|---|---|---|---|
| G33 | 50'000 | 802.807 | 802.80 (abgerundet) | 401.40 / 401.40 | 237.20 | A4 |
| G34 | 62'000 | 710.175 | 710.20 (aufgerundet) | 355.10 / 355.10 | 329.80 | A4 |
| G35 | 83'000 | 548.070 | 548.05 | 274.05 / 274.00 (Hälfte 274.025 aufgerundet, Gemeinde erhält den Rest) | 491.95 | A4 |

Hinweis für den Code: Mit Gleitkommazahlen kann 274.025 intern als 274.02499… erscheinen und falsch abgerundet werden. Vor dem Runden auf ganze Rappen runden oder eine kleine Toleranz verwenden.

### Beschäftigungsgrad (KiBG 4.1–4.2)

| Nr. | Änderung | `kibg_anspruch` | Status |
|---|---|---|---|
| G20 | Mutter allein, 20 % | ja | A6 |
| G21 | Mutter allein, 19 % | nein | A6 |
| G22 | Paar, 100 % + 20 % = 120 % | ja | fest |
| G23 | Paar, 100 % + 19 % = 119 % | nein | fest |
| G24 | Paar, 60 % + 60 % | ja | fest |
| G25 | Paar, 100 % + 0 %, Ausnahme bewilligt (`kibg_ausnahme_bewilligt`) | ja | fest |
| G32 | Paar, 110 % + 10 % = 120 % | nein (Vater unter 20 %) | Entscheid O3 |

### Lebensgemeinschaft (KiBV 8.2), ausgehend von P7

| Nr. | Änderung | `kibg_gefestigte_lebensgemeinschaft` | `kibg_massgebendes_einkommen` | Status |
|---|---|---|---|---|
| G26 | Konkubinat seit 2026-09-01 (genau 2 Jahre) | ja | 97'000 | A1 |
| G27 | Konkubinat seit 2026-09-02 | nein | 51'400 | A1 |
| G28 | verheiratet seit 2028-05-01 (Dauer egal) | ja | 97'000 | fest |

### Aktuelle Gegebenheiten (KiBG 5.4, KiBV 11), Mutter allein

Einkommen gemäss Steuerveranlagung 100'000.

| Nr. | Aktuelles Einkommen | Antrag | Abweichung | `kibg_massgebendes_einkommen` | Status |
|---|---|---|---|---|---|
| G29 | 75'000 | ja | 25 % | 75'000 | fest |
| G30 | 76'000 | ja | 24 % | 100'000 | fest |
| G31 | 70'000 | nein | 30 % | 100'000 | fest |

Höheres aktuelles Einkommen: siehe Q4.

---

## Teil 3: Kein Anspruch

Ausgehend von P1. Erwartet ist jeweils `kibg_anspruch` = nein und alle Beträge 0.

| Nr. | Änderung | Quelle | Status |
|---|---|---|---|
| X1 | Beide Eltern wohnen ausserhalb des Kantons | KiBG 4.1 | fest |
| X2 | Einrichtung nicht angemeldet | KiBG 3.3 | fest |
| X3 | Einrichtung nicht anerkannt | KiBG 3.2 | fest |
| X4 | Keine anerkannte Einrichtung (z. B. private Nanny), Typ `keine` | KiBG 3.2 | fest |
| X5 | Kind geboren 2016-05-01 (12 Jahre), Primarschule abgeschlossen | KiBG 4.3 | fest |
| X6 | Paar, 100 % + 0 %, keine Ausnahme | KiBG 4.1 | fest |

---

## Teil 4: Auslegungsfälle

Hier wären zwei Ergebnisse vertretbar. Das Team hat entschieden; die Fälle sind jetzt normale Tests und zugleich Material für die Stellungnahme.

| Nr. | Fall | Entscheid | Erwartet | Verworfene Lesart | Frage |
|---|---|---|---|---|---|
| Q1 | P1, Kind geboren 2027-03-01 (am 1. September 2028 genau 18 Monate) | Der tiefere Ansatz gilt ab dem 18-Monate-Geburtstag, also ab dem ersten Tag des 19. Lebensmonats; die vollen 18 Lebensmonate gilt der höhere | MaxV 7.50, Beitrag 300.00 | weiterhin 11.00 → 440.00 | O2 |
| Q2 | Paar, 120 % + 0 % | lit. a und b kumulativ: jeder Elternteil mindestens 20 % | Anspruch nein | nur die Summe zählt → Anspruch ja | O3 |
| Q3 | P1 mit Einkommen 160'000 und `kibg_zusatzbeitrag_z2` = 1.00 | Z2 ist einkommensunabhängig und gilt auch über 154'000; KiBV 15.2 betrifft nur den Mindestbeitrag | Mindestbeitrag 0.00, Zusatzbeitrag 80.00, Anteil Gemeinde 80.00 | kein Beitrag → 0.00 | O4 |
| Q4 | G29, aber aktuelles Einkommen 130'000 (+30 %), Antrag ja | Die Abweichung von 25 % zählt in beide Richtungen | `kibg_massgebendes_einkommen` 130'000 | nur Senkungen → 100'000 | O12 |

---

## Teil 5: Bekannte Einschränkung

| Nr. | Fall | Rechner | Nach Gesetz | Status |
|---|---|---|---|---|
| E1 | P1, aber 6 Tage pro Woche: 26 Tage, 260 Stunden, Kosten 3'380 | subventioniert 260 Stunden → 1'430.00 | höchstens 5 von 6 Tagen: rund 21.7 Tage, 216.7 Stunden → 1'191.65 (gerundet) | A3 |

Dieser Test belegt die dokumentierte Grenze: Der Rechner liefert hier bewusst den zu hohen Wert. Wird die Grenze später umgesetzt, muss der Test angepasst werden.

---

## Teil 6: Datumsregeln (optional)

Nur nötig, wenn `kibg_beitragsbeginn` programmiert wird. Ausgabe: ab welchem Datum Beiträge fliessen.

| Nr. | Betreuungsbeginn | Gesuch | `kibg_beitragsbeginn` | Quelle | Status |
|---|---|---|---|---|---|
| D1 | 2029-03-01 | 2029-03-31 (30 Tage später) | 2029-03-01 (rückwirkend) | KiBG 9.2 | fest |
| D2 | 2029-03-01 | 2029-04-01 (31 Tage später) | 2029-04-01 (ab Gesuch) | KiBG 9.2 | fest |
| D3 | 2028-08-01 (Vollzugsbeginn) | 2028-10-15 | 2028-08-01 (Übergangsfrist drei Monate) | KiBV 25.1 | fest |
| D4 | 2028-08-01 | 2028-11-15 | 2028-11-15 (ab Gesuch) | KiBG 9.2, KiBV 25.1 | fest |

Die Fälle von 2029 liegen bewusst ausserhalb der Übergangsfrist, damit nur KiBG 9.2 wirkt.

---

## Anhang: P1 als OpenFisca-Test

So wird ein Szenario zum Test. Die Rollennamen (`erziehungsberechtigte`, `kinder`) sind vorläufig und müssen mit Benjamins `entities.py` übereinstimmen.

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
        me_steuerveranlagung:
          2028: 60000
      vater:
        wohnsitz_kanton_sg: true
        beschaeftigungsgrad: 0.4
        me_steuerveranlagung:
          2028: 37000
      lina:
        geburtsdatum: 2027-09-01
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

## Kontrolle

Jede Rechnung soll eine zweite Person nachrechnen, bevor sie zum Test wird.

| Teil | Nachgerechnet von | Datum |
|---|---|---|
| Teil 1 (P1–P7b) | | |
| Teil 2 (G1–G35) | | |
| Teil 3 (X1–X6) | | |
| Teil 5–6 (E1, D1–D4) | | |
