// Verweise wie «KiBG 9 Abs. 2» oder «KiBV Anhang» in einen lesbaren Text und
// einen Link auf die Seite der PDF-Fassung übersetzen (static/quellen/).
// Sobald die neue Fassung in der Gesetzessammlung steht, nur hier umstellen.

const PDF = {
	KiBG: '/quellen/KiBG.pdf',
	KiBV: '/quellen/KiBV-Entwurf.pdf'
};

// Auf welcher PDF-Seite welcher Artikel beginnt
const SEITEN = {
	KiBG: [
		[1, 3],
		[2, 6],
		[3, 11],
		[4, 17],
		[5, 23]
	],
	KiBV: [
		[1, 4],
		[2, 9],
		[3, 14],
		[4, 17],
		[5, 21],
		[6, 23],
		[7, 25]
	]
};

const VRP = 'https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/951.1';

function seite(erlass, artikel) {
	if (artikel === 'Anhang') return 8;
	const nr = Number(artikel);
	const treffer = SEITEN[erlass].find(([, bis]) => nr <= bis);
	return treffer ? treffer[0] : 1;
}

/** «KiBG 9 Abs. 2» → { text: 'Art. 9 Abs. 2 KiBG', href: '/quellen/KiBG.pdf#page=3' } */
export function quelle(verweis) {
	if (verweis === 'VRP') return { text: 'VRP', href: VRP };
	const [, erlass, artikel, rest = ''] = verweis.match(/^(KiBG|KiBV) (\d+|Anhang)(.*)$/) ?? [];
	if (!erlass) return { text: verweis, href: null };
	const text = artikel === 'Anhang' ? `Anhang ${erlass}` : `Art. ${artikel}${rest} ${erlass}`;
	return { text, href: `${PDF[erlass]}#page=${seite(erlass, artikel)}` };
}
