# KiBG-Rechner (SvelteKit)

Oberfläche des Rechners: Fragebogen, Berechnen, Ergebnis. Gerechnet wird
ausschliesslich in OpenFisca (`../openfisca-CH-SG`); dieses Projekt setzt nur
die Werte in die Texte ein.

## Starten

Zwei Terminals:

```bash
# 1. OpenFisca-API (Port 5000)
cd openfisca-CH-SG && make serve-local

# 2. Oberfläche (http://localhost:5173)
cd frontend && npm install && npm run dev
```

Läuft die API anderswo, die Adresse setzen: `OPENFISCA_URL=http://… npm run dev`.

## Aufbau

| Datei | Inhalt |
|---|---|
| `src/lib/texte.de.json` | Alle Texte (Fragen, Hilfen, Ergebnis, Hinweise). Ohne Code bearbeitbar |
| `src/routes/+page.svelte` | Fragebogen (Haushalt, Erziehungsberechtigte, Kinder), Pflichtangaben, Berechnen |
| `src/lib/Feld.svelte`, `Auswahl.svelte` | Eingabefeld mit Info-Text beim Fokus; Auswahlknöpfe |
| `src/lib/Ergebnis.svelte` | Ergebnis pro Kind: Betrag, Voraussetzungen, Rechenweg, Hinweise |
| `src/lib/darstellung.js` | Werte formatieren und in Texte einsetzen; welche Texte erscheinen («wann») |
| `src/lib/server/situation.js` | Formular → OpenFisca-Situation; Antwort und Fehler auslesen (nur Server) |
| `src/routes/api/berechnen/+server.js` | Ruft OpenFisca `/calculate` auf; speichert nichts |
| `src/routes/+layout.svelte` | Kopfzeile und Farben (`--gruen` an einer Stelle) |

Design (Teamentscheid): sachlich, Weiss/Schwarz/Grün, Systemschrift, eine Seite
mit drei Abschnitten, grosse Auswahlknöpfe, Info-Text beim Fokus, Berechnen
immer klickbar mit Liste der fehlenden Angaben, Ergebnis im grünen Kasten mit
aufklappbaren Details. Das Grün nähert das Wappen-Grün an; kein Logo oder
Wappen, weil es ein Prototyp ist.

SvelteKit 3: Konfiguration in `vite.config.js`, Import-Alias `#lib`,
Umgebungsvariablen in `src/env.js`.
