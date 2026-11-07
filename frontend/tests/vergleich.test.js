// Tests für die Logik des Vergleichstools (src/lib/vergleich.js): Wochenplan
// mit Halbtagen, Pensum, Betreuung und Umrechnung in Monatswerte.
// Ausführen: npm test (Node, ohne weitere Pakete).

import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
	betreuungsplan,
	leererPlan,
	monatswerte,
	pensumAus,
	planBeiStufe,
	planMit,
	wochenwerte
} from '#lib/vergleich.js';

// Halbtage als Text: Mo VM, Mo NM, Di VM … ('X' = ja)
const text = (plan) => plan.map((ja) => (ja ? 'X' : '.')).join('');
const plan = (zeichen) => [...zeichen].map((z) => z === 'X');

test('1 Halbtag Arbeit = 10 % Pensum', () => {
	assert.equal(pensumAus(leererPlan()), 0);
	assert.equal(pensumAus(planMit(4)), 40);
	assert.equal(pensumAus(planMit(10)), 100);
});

test('mehr Pensum kommt ab Montag Vormittag dazu, nur in freie Halbtage', () => {
	const heute = plan('..XX......'); // Dienstag 20 %
	const { plan: neu, neu: markiert } = planBeiStufe(heute, 50);
	assert.equal(text(neu), 'XXXXX.....');
	assert.equal(text(markiert), 'XX..X.....');
	assert.equal(pensumAus(neu), 50);
});

test('weniger Pensum fällt ab Freitag Nachmittag weg', () => {
	const { plan: neu, neu: markiert } = planBeiStufe(planMit(10), 70);
	assert.equal(text(neu), 'XXXXXXX...');
	assert.equal(text(markiert), '..........');
});

test('gleiches Pensum lässt den Plan unverändert', () => {
	const heute = plan('X.X.X.....');
	assert.equal(text(planBeiStufe(heute, 30).plan), text(heute));
});

test('Betreuung nur, wenn alle Eltern arbeiten', () => {
	const vater = planMit(10);
	const mutter = plan('XXXX......');
	assert.equal(text(betreuungsplan([vater, mutter], leererPlan(), leererPlan())), 'XXXX......');
});

test('Alleinerziehend: Betreuung an jedem eigenen Arbeits-Halbtag', () => {
	const mutter = plan('XX..XX....');
	assert.equal(text(betreuungsplan([mutter], leererPlan(), leererPlan())), 'XX..XX....');
});

test('Hilfe (Grosseltern, Homeoffice) und Schulzeit ersetzen Betreuung', () => {
	const vater = planMit(10);
	const mutter = planMit(10);
	const hilfe = plan('...X......');
	const schule = plan('X.X.X.X.X.');
	assert.equal(text(betreuungsplan([vater, mutter], hilfe, schule)), '.X...X.X.X');
});

test('Tage und Halbtage pro Woche', () => {
	assert.deepEqual(wochenwerte(plan('XX.X......')), { tage: 2, halbtage: 3 });
	assert.deepEqual(wochenwerte(leererPlan()), { tage: 0, halbtage: 0 });
});

test('Monatswerte: 52 Wochen auf 12 Monate, Stunden pro Halbtag', () => {
	// 4 Halbtage à 5 Stunden = 20 Stunden pro Woche → 86.7 Stunden pro Monat
	assert.deepEqual(monatswerte({ tage: 2, halbtage: 4 }, 5), { tage: 9, stunden: 86.7 });
	// Tage aufgerundet: Die Grenze von 12 Stunden je Tag (Art. 14 Abs. 4 KiBV)
	// darf bei höchstens 6 Stunden je Halbtag nie greifen.
	const { tage, stunden } = monatswerte({ tage: 1, halbtage: 2 }, 6);
	assert.ok(tage * 12 >= stunden, `${tage} Tage, ${stunden} Stunden`);
});
