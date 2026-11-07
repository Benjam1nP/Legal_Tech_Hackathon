// Vergleich «Mehr arbeiten – welche Betreuung – was bleibt?» (Dashboard).
// Gemeinsame Logik für Seite und Server: Wochenplan mit Halbtagen, Pensen und
// Umrechnung der Betreuung in Monatswerte. Gerechnet wird der Beitrag nur in
// OpenFisca; hier stehen nur die Annahmen zur Betreuung.

// Wochenplan: Montag bis Freitag, je Vormittag und Nachmittag = 10 Halbtage.
// Ein Halbtag Arbeit entspricht 10 % Pensum (10 Halbtage = 100 %).
export const TAGE = ['Mo', 'Di', 'Mi', 'Do', 'Fr'];
export const HALBTAGE = 10;
export const leererPlan = () => Array(HALBTAGE).fill(false);
export const tagVon = (halbtag) => Math.floor(halbtag / 2);

/** Pensum in Prozent aus den Arbeits-Halbtagen. */
export const pensumAus = (plan) => plan.filter(Boolean).length * 10;

/** Plan mit den ersten n Halbtagen (Montag Vormittag zuerst). */
export const planMit = (anzahl) => leererPlan().map((_, i) => i < anzahl);

// Pensumstufen der variierten Person: 0 bis 100 % in Halbtagen.
export const STUFEN = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100];

/**
 * Plan der variierten Person bei einem anderen Pensum: Ausgehend vom heutigen
 * Plan kommen Halbtage von Montag Vormittag an dazu (erst die freien), oder
 * sie fallen von Freitag Nachmittag an weg. `neu` markiert hinzugekommene
 * Halbtage.
 */
export function planBeiStufe(heute, stufe) {
	const ziel = Math.round(stufe / 10);
	const plan = [...heute];
	const neu = leererPlan();
	let anzahl = plan.filter(Boolean).length;
	for (let i = 0; i < HALBTAGE && anzahl < ziel; i++) {
		if (!plan[i]) {
			plan[i] = true;
			neu[i] = true;
			anzahl++;
		}
	}
	for (let i = HALBTAGE - 1; i >= 0 && anzahl > ziel; i--) {
		if (plan[i]) {
			plan[i] = false;
			anzahl--;
		}
	}
	return { plan, neu };
}

/**
 * Halbtage, in denen ein Kind betreut werden muss: Alle Eltern im Haushalt
 * arbeiten, niemand sonst hilft (Grosseltern, Homeoffice …) und das Kind ist
 * nicht in der Schule oder im Kindergarten.
 */
export function betreuungsplan(elternPlaene, hilfe, schule) {
	return leererPlan().map(
		(_, i) => elternPlaene.every((plan) => plan[i]) && !hilfe[i] && !schule[i]
	);
}

/** Betreuungstage und -halbtage pro Woche aus einem Betreuungsplan. */
export function wochenwerte(plan) {
	const tage = new Set(plan.map((ja, i) => (ja ? tagVon(i) : null)).filter((t) => t !== null));
	return { tage: tage.size, halbtage: plan.filter(Boolean).length };
}

// Betreuungsformen, die verglichen werden. Schulergänzende Betreuung nur für
// eingeschulte Kinder (Art. 14 Abs. 3 KiBV; Teamentscheid: setzt die Schulzeit
// voraus).
export const FORMEN = ['kita', 'tagesfamilie', 'schulergaenzend'];
export const formenFuer = (kind) =>
	kind.eingeschult ? FORMEN : FORMEN.filter((form) => form !== 'schulergaenzend');

// Vorbelegte Preise (Fr. pro Stunde) und Stunden pro Halbtag; änderbar.
// Höchstens 6 Stunden pro Halbtag, damit ein Tag nie über 12 Stunden kommt
// (Art. 14 Abs. 4 KiBV).
export const VORGABE_PREIS = { kita: 13, tagesfamilie: 10.5, schulergaenzend: 9 };
export const VORGABE_STUNDEN = { kita: 5, tagesfamilie: 4.5, schulergaenzend: 3 };
export const MAX_STUNDEN_HALBTAG = 6;

// 52 Wochen auf 12 Monate.
export const WOCHEN_PRO_MONAT = 52 / 12;

/** Monatswerte für OpenFisca aus den Werten pro Woche. */
export function monatswerte({ tage, halbtage }, stundenProHalbtag) {
	// Tage aufrunden: Sie dienen nur der Grenze von 12 Stunden je Tag
	// (Art. 14 Abs. 4 KiBV), die mit höchstens 6 Stunden je Halbtag nie greift.
	return {
		tage: Math.ceil(tage * WOCHEN_PRO_MONAT),
		stunden: Math.round(halbtage * Number(stundenProHalbtag) * WOCHEN_PRO_MONAT * 10) / 10
	};
}
