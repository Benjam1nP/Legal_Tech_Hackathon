// Zusammenspiel Frontend–OpenFisca: Die Angaben werden so an OpenFisca
// geschickt, wie Rechner und Vergleichstool sie bauen; die erwarteten Werte
// stammen aus challenge/szenarien.md.
//
// Braucht eine laufende OpenFisca-API (make serve-local). Adresse über
// OPENFISCA_URL, sonst http://127.0.0.1:5000. Ohne API werden die Tests
// übersprungen.
//   OPENFISCA_URL=http://127.0.0.1:5001 npm test

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { situation, ergebnisse, fehlerliste } from '#lib/server/situation.js';
import * as vergleich from '#lib/server/vergleich.js';
import { betreuungsplan, leererPlan, planMit, wochenwerte, STUFEN } from '#lib/vergleich.js';

const URL = process.env.OPENFISCA_URL ?? 'http://127.0.0.1:5000';
const erreichbar = await fetch(`${URL}/spec`)
	.then((r) => r.ok)
	.catch(() => false);
const api = { skip: erreichbar ? false : `OpenFisca nicht erreichbar unter ${URL}` };

async function rechnen(daten) {
	const antwort = await fetch(`${URL}/calculate`, {
		method: 'POST',
		headers: { 'Content-Type': 'application/json' },
		body: JSON.stringify(daten)
	});
	return { status: antwort.status, inhalt: await antwort.json() };
}

/** Angaben wie im Rechner; Familie P1 (szenarien.md), mit Änderungen. */
function p1(aenderung = {}) {
	const kind = {
		geburtsdatum: '2027-09-01',
		betreuungsbeginn: '2028-08-01',
		gesuchsdatum: '2028-08-15',
		eingeschult: false,
		primarschuleAbgeschlossen: false,
		typ: 'kita',
		anerkannt: true,
		angemeldet: true,
		bestaetigtAm: '',
		jahrKindergarten: null,
		tage: 8,
		stunden: 80,
		kosten: 1040,
		...(aenderung.kind ?? {})
	};
	return {
		monat: '2028-09',
		gemeinsam: true,
		gesuchsteller: 0,
		eltern: [
			{ wohnsitz: true, pensum: 100, einkommen: 60000, aktuell: null },
			{ wohnsitz: true, pensum: 40, einkommen: 37000, aktuell: null }
		],
		partner: { vorhanden: false },
		antragAktuell: false,
		ausnahme: false,
		kinder: [kind],
		...aenderung,
		...(aenderung.kind ? { kinder: [kind] } : {})
	};
}

/** Familie P7: getrennter Vater mit Partnerin im Konkubinat. */
function p7(seit) {
	return {
		...p1({
			kind: { geburtsdatum: '2024-09-01', tage: 8, stunden: 72, kosten: 864 }
		}),
		gemeinsam: false,
		eltern: [{ wohnsitz: true, pensum: 80, einkommen: 51400, aktuell: null }],
		partner: { vorhanden: true, einkommen: 45600, verheiratet: false, seit }
	};
}

async function rechner(angaben) {
	const { status, inhalt } = await rechnen(situation(angaben));
	assert.equal(status, 200, JSON.stringify(inhalt));
	return ergebnisse(inhalt, angaben);
}

test('Rechner P1: Fr. 440 Beitrag, Fr. 600 Restkosten', api, async () => {
	const { haushalt, kinder } = await rechner(p1());
	assert.equal(haushalt.kibg_massgebendes_einkommen, 97000);
	assert.equal(haushalt.kibg_einkommensfaktor, 0.5);
	assert.equal(kinder[0].kibg_beitrag_total, 440);
	assert.equal(kinder[0].kibg_restkosten_eltern, 600);
	assert.equal(kinder[0].kibg_beitragsbeginn, '2028-08-01');
	assert.equal(kinder[0].kibg_verfuegung_ende, '2029-07-31');
});

test('Rechner P2: Alleinerziehende, Tagesfamilie, Fr. 594', api, async () => {
	const angaben = p1({
		kind: { geburtsdatum: '2026-03-01', typ: 'tagesfamilie', tage: 12, stunden: 108, kosten: 1134 }
	});
	angaben.gemeinsam = false;
	angaben.eltern = [{ wohnsitz: true, pensum: 50, einkommen: 30000, aktuell: null }];
	const { kinder } = await rechner(angaben);
	assert.equal(kinder[0].kibg_beitrag_total, 594);
	assert.equal(kinder[0].kibg_restkosten_eltern, 540);
});

test('Rechner P6: Kostenobergrenze, Beitrag = Kosten Fr. 900', api, async () => {
	const angaben = p1({ kind: { geburtsdatum: '2028-01-01', tage: 10, stunden: 100, kosten: 900 } });
	angaben.gemeinsam = false;
	angaben.eltern = [{ wohnsitz: true, pensum: 60, einkommen: 40000, aktuell: null }];
	const { kinder } = await rechner(angaben);
	assert.equal(kinder[0].kibg_beitrag_total, 900);
	assert.equal(kinder[0].kibg_restkosten_eltern, 0);
});

test('Rechner P7 und P7b: Partnerin zählt erst nach zwei Jahren', api, async () => {
	const p7Ergebnis = await rechner(p7('2026-01-01'));
	assert.equal(p7Ergebnis.partnerEinkommenZaehlt, true);
	assert.equal(p7Ergebnis.haushalt.kibg_massgebendes_einkommen, 97000);
	assert.equal(p7Ergebnis.kinder[0].kibg_beitrag_total, 270);
	const p7b = await rechner(p7('2027-06-01'));
	assert.equal(p7b.partnerEinkommenZaehlt, false);
	assert.equal(p7b.kinder[0].kibg_beitrag_total, 486);
});

test('Rechner G16: Kind noch keine 3 Monate, volle Restkosten', api, async () => {
	const { kinder } = await rechner(p1({ kind: { geburtsdatum: '2028-06-02' } }));
	assert.equal(kinder[0].kibg_anspruch, false);
	assert.equal(kinder[0].kibg_alter_erfuellt, false);
	assert.equal(kinder[0].kibg_restkosten_eltern, 1040);
});

test('Rechner Q2: Paar 120 % + 0 %, kein Anspruch (lit. a und b kumulativ)', api, async () => {
	const angaben = p1();
	angaben.eltern[0].pensum = 120;
	angaben.eltern[1].pensum = 0;
	const { haushalt, kinder } = await rechner(angaben);
	assert.equal(haushalt.kibg_beschaeftigung_lit_a_erfuellt, false);
	assert.equal(haushalt.kibg_beschaeftigung_lit_b_erfuellt, true);
	assert.equal(kinder[0].kibg_anspruch, false);
});

test('Rechner: Ein Elternteil im Kanton genügt, wenn er als gesuchstellend gilt', api, async () => {
	const angaben = p1();
	angaben.eltern[0].wohnsitz = false;
	angaben.gesuchsteller = 1; // wie im Rechner: erste Person mit Wohnsitz im Kanton
	const { haushalt, kinder } = await rechner(angaben);
	assert.equal(haushalt.kibg_wohnsitz_erfuellt, true);
	assert.equal(kinder[0].kibg_beitrag_total, 440);
});

test('Rechner D2: Gesuch 31 Tage nach Betreuungsbeginn, im März kein Beitrag', api, async () => {
	const angaben = p1({
		monat: '2029-03',
		kind: { betreuungsbeginn: '2029-03-01', gesuchsdatum: '2029-04-01' }
	});
	const { kinder } = await rechner(angaben);
	assert.equal(kinder[0].kibg_beitragsbeginn, '2029-04-01');
	assert.equal(kinder[0].kibg_anspruch, false);
	assert.equal(kinder[0].kibg_beitrag_total, 0);
});

test('Rechner D13: Nach zwölf Monaten braucht es ein neues Gesuch', api, async () => {
	const { kinder } = await rechner(p1({ monat: '2029-08' }));
	assert.equal(kinder[0].kibg_verfuegung_laeuft, false);
	assert.equal(kinder[0].kibg_anspruch, false);
});

test('Rechner F1: Ohne Geburtsdatum Fehler beim richtigen Feld', api, async () => {
	const { status, inhalt } = await rechnen(situation(p1({ kind: { geburtsdatum: '' } })));
	assert.equal(status, 400);
	const liste = fehlerliste(inhalt);
	assert.ok(
		liste.some((f) => f.pfad === 'persons/kind_1/geburtsdatum'),
		JSON.stringify(liste)
	);
});

test('Rechner: Leere Daten führen zu einem Fehler, nicht zu einem Beitrag', api, async () => {
	for (const feld of ['betreuungsbeginn', 'gesuchsdatum']) {
		const { status, inhalt } = await rechnen(situation(p1({ kind: { [feld]: '' } })));
		assert.equal(status, 400, `${feld}: ${JSON.stringify(inhalt).slice(0, 200)}`);
	}
});

// --- Vergleichstool ---------------------------------------------------------

/** Angaben wie im Vergleichstool: P1, Person 2 variiert, Wochenplan. */
function vergleichAngaben() {
	const eltern = [planMit(10), planMit(4)];
	const kind = {
		geburtsdatum: '2027-09-01',
		eingeschult: false,
		form: 'kita',
		preise: { kita: 13, tagesfamilie: 10.5, schulergaenzend: 9 },
		stunden: { kita: 5, tagesfamilie: 4.5, schulergaenzend: 3 }
	};
	const betreuung = Object.fromEntries(
		STUFEN.map((s) => {
			const plaene = [eltern[0], planMit(s / 10)];
			return [s, [wochenwerte(betreuungsplan(plaene, leererPlan(), leererPlan()))]];
		})
	);
	return {
		monat: '2028-09',
		variiert: 1,
		lohn100: 7000,
		vergleichKind: 0,
		eltern: [
			{ pensum: 100, einkommen: 60000 },
			{ pensum: 40, einkommen: 37000 }
		],
		kinder: [kind],
		betreuung
	};
}

async function vergleichen(angaben) {
	const liste = vergleich.faelle(angaben);
	const { status, inhalt } = await rechnen(vergleich.situation(angaben, liste));
	assert.equal(status, 200, JSON.stringify(inhalt));
	return vergleich.auswerten(inhalt, angaben, liste);
}

test('Vergleichstool: ein Fall je Pensumstufe und Betreuungsform', () => {
	const liste = vergleich.faelle(vergleichAngaben());
	// heute + 11 Stufen × 2 Formen (Kita, Tagesfamilie; Kind nicht eingeschult)
	assert.equal(liste.length, 1 + 11 * 2);
});

test('Vergleichstool: heute gleich wie der Rechner mit denselben Monatswerten', api, async () => {
	const ergebnis = await vergleichen(vergleichAngaben());
	// Heute 40 %: Montag und Dienstag, 4 Halbtage à 5 Stunden = 86.7 Stunden
	const rechnerErgebnis = await rechner(p1({ kind: { tage: 9, stunden: 86.7, kosten: 86.7 * 13 } }));
	assert.equal(ergebnis.ausgangslage.beitrag, rechnerErgebnis.kinder[0].kibg_beitrag_total);
	assert.equal(ergebnis.ausgangslage.beitrag, 476.85);
	assert.equal(ergebnis.ausgangslage.restkosten, 650.25);
});

test('Vergleichstool: unter 20 % kein Anspruch, bei 0 % keine Kosten', api, async () => {
	const { ergebnisse: alle } = await vergleichen(vergleichAngaben());
	const fall = (stufe) => alle.find((e) => e.form === 'kita' && e.stufe === stufe);
	assert.equal(fall(0).restkosten, 0);
	assert.equal(fall(10).anspruch, false);
	assert.equal(fall(10).litA, false);
	// Kosten gehen als Gleitkommazahl hin, OpenFisca rechnet mit float32
	assert.ok(Math.abs(fall(10).restkosten - fall(10).kinder[0].kosten) < 0.01);
	assert.equal(fall(20).anspruch, true);
});

test('Vergleichstool: mehr Pensum, mehr Betreuung, höherer Beitrag (gleiches Einkommen)', api, async () => {
	const { ergebnisse: alle } = await vergleichen(vergleichAngaben());
	const kita = STUFEN.filter((s) => s >= 20).map(
		(s) => alle.find((e) => e.form === 'kita' && e.stufe === s).beitrag
	);
	for (let i = 1; i < kita.length; i++) assert.ok(kita[i] >= kita[i - 1], kita.join(', '));
});
