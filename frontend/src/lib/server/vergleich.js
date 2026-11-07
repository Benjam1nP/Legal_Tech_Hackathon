// Baut für den Vergleich im Dashboard eine Situation mit vielen Haushalten:
// einen Haushalt je Pensumstufe × Betreuungsform. OpenFisca rechnet alle in
// einer Anfrage (/calculate). Das massgebende Einkommen bleibt wie in der
// letzten Steuerveranlagung (Art. 5 Abs. 3 KiBG).
//
// Annahmen, damit nur Pensum und Betreuung den Unterschied machen: Wohnsitz
// im Kanton, Einrichtung anerkannt und angemeldet, Gesuch rechtzeitig
// (Betreuungsbeginn und Gesuch am Monatsersten), keine Zusatzbeiträge der
// Gemeinde. Bei zwei Eltern stellt Elternteil 1 das Gesuch.

import { STUFEN, formenFuer, monatswerte } from '#lib/vergleich.js';

const ERGEBNISSE_KIND = [
	'kibg_anspruch',
	'kibg_hoechstbeitrag',
	'kibg_beitrag_total',
	'kibg_restkosten_eltern'
];
const ERGEBNISSE_HAUSHALT = [
	'kibg_beschaeftigung_lit_a_erfuellt',
	'kibg_beschaeftigung_lit_b_erfuellt',
	'kibg_beschaeftigung_erfuellt',
	'kibg_massgebendes_einkommen'
];

const zahl = (wert) => Number(wert);

/**
 * Betreuung pro Woche für ein Kind auf einer Pensumstufe, aus dem Wochenplan
 * der Seite: { tage, halbtage }.
 */
function betreuungProWoche(angaben, stufe, kindIndex) {
	return angaben.betreuung?.[stufe]?.[kindIndex] ?? { tage: 0, halbtage: 0 };
}

/** Alle Fälle, die gerechnet werden: je Stufe und Form des Vergleichskinds. */
export function faelle(angaben) {
	const heute = zahl(angaben.eltern[angaben.variiert].pensum);
	const formen = formenFuer(angaben.kinder[angaben.vergleichKind]);
	// Ausgangslage: heutiges Pensum und heutige Betreuung (auch «keine»).
	const kind = angaben.kinder[angaben.vergleichKind];
	const liste = [{ id: 'fall_heute', form: kind.form, stufe: heute }];
	for (const form of formen) {
		for (const stufe of STUFEN) {
			liste.push({ id: `fall_${liste.length}`, form, stufe });
		}
	}
	return liste;
}

/** Situation im Format der OpenFisca-Web-API mit einem Haushalt je Fall. */
export function situation(angaben, liste) {
	const monat = angaben.monat;
	const jahr = monat.slice(0, 4);
	const tag = `${monat}-01`;
	const persons = {};
	const households = {};

	for (const fall of liste) {
		const eltern = angaben.eltern.map((person, index) => {
			const id = `${fall.id}_elternteil_${index + 1}`;
			const variiert = index === angaben.variiert;
			const pensum = variiert ? fall.stufe : zahl(person.pensum);
			persons[id] = {
				wohnsitz_kanton_sg: { [monat]: true },
				beschaeftigungsgrad: { [monat]: pensum / 100 },
				me_steuerveranlagung: { [jahr]: zahl(person.einkommen) }
			};
			if (angaben.eltern.length === 2 && index === 0) {
				persons[id].kibg_gesuchstellend = { [monat]: true };
			}
			return id;
		});

		const kinder = angaben.kinder.map((kind, index) => {
			const id = `${fall.id}_kind_${index + 1}`;
			const form = index === angaben.vergleichKind ? fall.form : kind.form;
			// «keine»: Die Eltern betreuen selbst, es entstehen keine Kosten.
			const betreut = form !== 'keine';
			const monat_ = betreut
				? monatswerte(betreuungProWoche(angaben, fall.stufe, index), kind.stunden[form])
				: { tage: 0, stunden: 0 };
			const tage = monat_.tage;
			const stunden = monat_.stunden;
			persons[id] = {
				geburtsdatum: { ETERNITY: kind.geburtsdatum },
				betreuungsbeginn: { ETERNITY: tag },
				kibg_gesuchsdatum: { ETERNITY: tag },
				eingeschult: { [monat]: kind.eingeschult === true },
				primarschule_abgeschlossen: { [monat]: false },
				kibg_einrichtungstyp: { [monat]: form },
				kibg_einrichtung_anerkannt: { [monat]: true },
				kibg_einrichtung_angemeldet: { [monat]: true },
				betreuungstage_mit_obhut: { [monat]: tage },
				betreuungsstunden: { [monat]: stunden },
				kibg_betreuungskosten: { [monat]: betreut ? stunden * zahl(kind.preise[form]) : 0 },
				...Object.fromEntries(ERGEBNISSE_KIND.map((n) => [n, { [monat]: null }]))
			};
			return id;
		});

		households[fall.id] = {
			erziehungsberechtigte: eltern,
			kinder,
			gemeinsamer_haushalt: { [monat]: angaben.eltern.length === 2 },
			...Object.fromEntries(ERGEBNISSE_HAUSHALT.map((n) => [n, { [monat]: null }]))
		};
	}
	return { persons, households };
}

/** Fasst die Antwort pro Fall zusammen (Summen über alle Kinder). */
export function auswerten(antwort, angaben, liste) {
	const monat = angaben.monat;
	const wert = (eintrag, name) => eintrag[name]?.[monat];
	const heute = Math.round(zahl(angaben.eltern[angaben.variiert].pensum));

	const alle = liste.map((fall) => {
		const haushalt = antwort.households[fall.id];
		const kinder = angaben.kinder.map((_, index) => {
			const person = antwort.persons[`${fall.id}_kind_${index + 1}`];
			const kosten = person.kibg_betreuungskosten?.[monat];
			return {
				anspruch: wert(person, 'kibg_anspruch'),
				hoechstbeitrag: wert(person, 'kibg_hoechstbeitrag'),
				beitrag: wert(person, 'kibg_beitrag_total'),
				restkosten: wert(person, 'kibg_restkosten_eltern'),
				kosten
			};
		});
		const summe = (feld) => kinder.reduce((s, k) => s + zahl(k[feld] ?? 0), 0);
		return {
			...fall,
			beitrag: summe('beitrag'),
			restkosten: summe('restkosten'),
			anspruch: kinder.some((k) => k.anspruch),
			kinder,
			litA: wert(haushalt, 'kibg_beschaeftigung_lit_a_erfuellt'),
			litB: wert(haushalt, 'kibg_beschaeftigung_lit_b_erfuellt'),
			beschaeftigung: wert(haushalt, 'kibg_beschaeftigung_erfuellt'),
			einkommen: wert(haushalt, 'kibg_massgebendes_einkommen')
		};
	});

	const ausgangslage = alle.find((e) => e.id === 'fall_heute');
	const ergebnisse = alle.filter((e) => e.id !== 'fall_heute');
	return { heute, ausgangslage, ergebnisse };
}
