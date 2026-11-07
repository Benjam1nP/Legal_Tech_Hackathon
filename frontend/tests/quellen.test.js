// Artikelverweise (src/lib/quellen.js) zeigen auf Sprungmarken, die es im
// Wortlaut von Gesetz und Verordnung (src/lib/recht/*.md) wirklich gibt.

import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { quelle } from '#lib/quellen.js';

const lesen = (pfad) => readFileSync(new URL(pfad, import.meta.url), 'utf8');
const marken = new Set(
	[lesen('../src/lib/recht/kibg.md'), lesen('../src/lib/recht/kibv.md')].flatMap((md) =>
		[...md.matchAll(/<a id="([^"]+)"><\/a>/g)].map((m) => m[1])
	)
);

test('Verweise werden zu Text und Sprungmarke', () => {
	assert.deepEqual(quelle('KiBG 9 Abs. 2'), {
		text: 'Art. 9 Abs. 2 KiBG',
		href: '/gesetzgebung#kibg-art-9-abs-2'
	});
	assert.equal(quelle('KiBV 14').href, '/gesetzgebung#kibv-art-14');
	assert.equal(quelle('KiBG 4 Abs. 1 lit. b').href, '/gesetzgebung#kibg-art-4-abs-1-lit-b');
	assert.deepEqual(quelle('KiBV Anhang'), { text: 'Anhang KiBV', href: '/gesetzgebung#kibv-anhang' });
	assert.equal(quelle('irgendwas').href, null);
});

test('Jeder Verweis im Ablauf hat eine Sprungmarke im Gesetzestext', () => {
	const ablauf = lesen('../src/lib/ablauf.de.json');
	const verweise = [...ablauf.matchAll(/"((?:KiBG|KiBV) [^"]+)"/g)].map((m) => m[1]);
	assert.ok(verweise.length > 30, `nur ${verweise.length} Verweise gefunden`);
	const fehlend = verweise.filter((v) => !marken.has(quelle(v).href.split('#')[1]));
	assert.deepEqual(fehlend, []);
});

test('Gesetz und Verordnung: alle Artikel haben eine Sprungmarke', () => {
	for (let nr = 1; nr <= 23; nr++) assert.ok(marken.has(`kibg-art-${nr}`), `KiBG ${nr}`);
	for (let nr = 1; nr <= 25; nr++) assert.ok(marken.has(`kibv-art-${nr}`), `KiBV ${nr}`);
});
