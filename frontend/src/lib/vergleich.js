// Vergleich «Mehr arbeiten – welche Betreuung – was bleibt?» (Dashboard).
// Gemeinsame Logik für Seite und Server: Pensumstufen, Vorschlag für die
// Betreuungstage und Umrechnung in Monatswerte. Gerechnet wird der Beitrag
// nur in OpenFisca; hier stehen nur die Annahmen zur Betreuung.

// Pensumstufen der variierten Person in Prozent.
export const STUFEN = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100];

// Betreuungsformen, die verglichen werden. Schulergänzende Betreuung nur für
// eingeschulte Kinder (Art. 14 Abs. 3 KiBV; Teamentscheid: setzt die Schulzeit
// voraus).
export const FORMEN = ['kita', 'tagesfamilie', 'schulergaenzend'];
export const formenFuer = (kind) =>
	kind.eingeschult ? FORMEN : FORMEN.filter((form) => form !== 'schulergaenzend');

// Vorbelegte Preise (Fr. pro Stunde) und Stunden pro Betreuungstag; änderbar.
export const VORGABE_PREIS = { kita: 13, tagesfamilie: 10.5, schulergaenzend: 9 };
export const VORGABE_STUNDEN = { kita: 10, tagesfamilie: 9, schulergaenzend: 3 };

// 52 Wochen auf 12 Monate.
const WOCHEN_PRO_MONAT = 52 / 12;

/** Arbeitstage pro Woche bei einem Pensum in Prozent (100 % = 5 Tage). */
export const arbeitstage = (pensum) => Math.min(5, Math.max(0, Number(pensum) / 20));

/**
 * Vorschlag für die Betreuungstage pro Woche (Teamentscheid, Variante c mit
 * der Annahme von Variante a): Alleinerziehende brauchen an jedem eigenen
 * Arbeitstag Betreuung; bei Paaren an den Arbeitstagen der Person, die weniger
 * arbeitet (die Arbeitstage überlappen). Die Eltern können jeden Wert ändern.
 */
export function vorschlagTage(pensumVariiert, pensumAndere, paar) {
	const eigene = arbeitstage(pensumVariiert);
	return paar ? Math.min(eigene, arbeitstage(pensumAndere)) : eigene;
}

/** Betreuungstage im Monat aus Tagen pro Woche (ganze Tage). */
export const tageImMonat = (tageProWoche) =>
	Math.round(Math.max(0, Number(tageProWoche)) * WOCHEN_PRO_MONAT);

/** Stufen inklusive heutigem Pensum, falls es kein Vielfaches von 10 ist. */
export function stufenMit(heute) {
	const p = Math.round(Number(heute));
	return STUFEN.includes(p) ? STUFEN : [...STUFEN, p].sort((a, b) => a - b);
}
