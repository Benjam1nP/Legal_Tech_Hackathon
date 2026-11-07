// Verweise wie «KiBG 9 Abs. 2» oder «KiBV Anhang» in einen lesbaren Text und
// einen Link auf die Stelle im Tab «Gesetzgebung» übersetzen. Dort hat jeder
// Artikel, Absatz und Buchstabe eine Sprungmarke (src/lib/recht/*.md), z. B.
// /gesetzgebung#kibg-art-9-abs-2. Die PDF-Fassungen liegen in static/quellen/.

const VRP = 'https://www.gesetzessammlung.sg.ch/app/de/texts_of_law/951.1';

/** Sprungmarke im Tab «Gesetzgebung», z. B. kibg-art-9-abs-2 oder kibv-anhang. */
export function sprungmarke(erlass, artikel, rest = '') {
	const kuerzel = erlass.toLowerCase();
	if (artikel === 'Anhang') return `${kuerzel}-anhang`;
	const abs = rest.match(/Abs\. (\d+)/)?.[1];
	const lit = rest.match(/lit\. ([a-z])/)?.[1];
	return [`${kuerzel}-art-${artikel}`, abs && `abs-${abs}`, abs && lit && `lit-${lit}`]
		.filter(Boolean)
		.join('-');
}

/** «KiBG 9 Abs. 2» → { text: 'Art. 9 Abs. 2 KiBG', href: '/gesetzgebung#kibg-art-9-abs-2' } */
export function quelle(verweis) {
	if (verweis === 'VRP') return { text: 'VRP', href: VRP };
	const [, erlass, artikel, rest = ''] = verweis.match(/^(KiBG|KiBV) (\d+|Anhang)(.*)$/) ?? [];
	if (!erlass) return { text: verweis, href: null };
	const text = artikel === 'Anhang' ? `Anhang ${erlass}` : `Art. ${artikel}${rest} ${erlass}`;
	return { text, href: `/gesetzgebung#${sprungmarke(erlass, artikel, rest)}` };
}
