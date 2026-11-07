# KiBG-Rechner (SvelteKit)

Oberfläche des Rechners: Fragebogen, Berechnen, Ergebnis. Gerechnet wird
ausschliesslich in OpenFisca (`../openfisca-CH-SG`); dieses Projekt setzt nur
die Werte in die Texte ein.

## Starten

Zwei Terminals:

```bash
# 1. OpenFisca-API (Port 5000)
cd openfisca-CH-SG && make serve-local

# 2. Oberfläche (http://localhost:5173, Rechner unter /rechner)
cd frontend && npm install && npm run dev
```

Läuft die API anderswo, die Adresse setzen: `OPENFISCA_URL=http://… npm run dev`.
Auf macOS ist Port 5000 oft durch AirPlay belegt. Dann die API mit
`uv run openfisca serve --country-package openfisca_ch_sg --port 5001` starten und
`OPENFISCA_URL=http://127.0.0.1:5001 npm run dev` verwenden.

## Aufbau

| Datei | Inhalt |
|---|---|
| `src/lib/texte.de.json` | Alle Texte (Fragen, Hilfen, Ergebnis, Hinweise). Ohne Code bearbeitbar |
| `src/routes/+page.svelte` | Tab «Home» (`/`), noch leer |
| `src/routes/rechner/+page.svelte` | Tab «Rechner» (`/rechner`): Fragebogen (Haushalt, Erziehungsberechtigte, Kinder), Pflichtangaben, Berechnen |
| `src/routes/dashboard/+page.svelte` | Tab «Dashboard» (`/dashboard`): Vergleich «Mehr arbeiten – welche Betreuung – was bleibt?». Pensum einer frei wählbaren Person × Betreuungsform (Kita, Tagesfamilie, schulergänzend), mit dem Einkommen laut letzter Steuerveranlagung; Wochenplan, Kennzahlen, Linien- und Balken-Chart, Tabelle |
| `src/routes/gesuch/+page.svelte` | Tab «Gesuch stellen» (`/gesuch`): Ablauf der Gesuchstellung in 6 Schritten als Diagramm, je Schritt «Sie tun» und «Das passiert ohne Sie», Zeitstrahl der 30-Tage-Frist |
| `src/lib/ablauf.de.json` | Texte des Ablaufs mit Artikelverweisen. Ohne Code bearbeitbar |
| `src/lib/quellen.js`, `src/lib/Quelle.svelte` | Verweis wie «KiBG 9 Abs. 2» → Link auf die PDF-Seite in `static/quellen/` (KiBG, KiBV-Entwurf) |
| `src/lib/vergleich.js` | Wochenplan mit Halbtagen (Mo–Fr, Vormittag und Nachmittag; 1 Halbtag = 10 % Pensum): Betreuung nötig, wenn alle Eltern arbeiten, niemand sonst hilft und das Kind nicht in der Schule ist; Pläne bei anderem Pensum (dazu ab Montag Vormittag, weg ab Freitag Nachmittag); Umrechnung in Monatswerte; Vorgaben für Preise und Stunden pro Halbtag |
| `src/lib/Wochenplan.svelte` | Wochenplan zum Anklicken (heute) und zur Anzeige (beim neuen Pensum); auf dem Handy mit Titel über der Zeile |
| `src/lib/server/vergleich.js` | Ein Haushalt je Stufe × Form in einer OpenFisca-Anfrage; Annahmen: Wohnsitz, anerkannte und angemeldete Einrichtung, rechtzeitiges Gesuch, keine Zusatzbeiträge, ohne Steuern |
| `src/routes/api/vergleich/+server.js` | Ruft OpenFisca `/calculate` für den Vergleich auf; speichert nichts |
| `src/lib/LinienChart.svelte`, `BalkenChart.svelte` | Charts als SVG, ohne zusätzliche Bibliothek |
| `src/lib/Feld.svelte`, `Auswahl.svelte` | Eingabefeld mit Info-Text beim Fokus; Auswahlknöpfe |
| `src/lib/Ergebnis.svelte` | Ergebnis pro Kind: Betrag, Voraussetzungen, Rechenweg, Hinweise |
| `src/lib/darstellung.js` | Werte formatieren und in Texte einsetzen; welche Texte erscheinen («wann») |
| `src/lib/server/situation.js` | Formular → OpenFisca-Situation; Antwort und Fehler auslesen (nur Server) |
| `src/routes/api/berechnen/+server.js` | Ruft OpenFisca `/calculate` auf; speichert nichts |
| `src/app.css` | Design-Tokens: Farben, Schrift, Abstände (Grün an einer Stelle) |
| `src/routes/+layout.svelte` | Kopfzeile und Tabs (Namen in `texte.de.json`, `navigation`) |

Design: nach dem Style-Kit (`style-kit/STYLE.md`), schlank umgesetzt, ohne
Tailwind oder shadcn. Tokens in `src/app.css`: nur hell, neutrale Grautöne,
Ebenen durch Fläche und 1px-Linie statt Schatten, Rundung 8px, Schrift Geist,
Beträge in Geist Mono, kleine Überschriften in Grossbuchstaben. Einzige
Akzentfarbe ist das Grün des Kantons St. Gallen (`--primary`, `--gruen-wappen`
in `app.css`; offiziellen Farbcode dort einsetzen): Hauptknopf, Auswahl, Fokus,
Ergebnis. Eine Seite mit drei Abschnitten als Karten, Info-Text beim Fokus,
Berechnen immer klickbar mit Liste der fehlenden Angaben. Kein Logo oder
Wappen, weil es ein Prototyp ist.

SvelteKit 3: Konfiguration in `vite.config.js`, Import-Alias `#lib`,
Umgebungsvariablen in `src/env.js`.
