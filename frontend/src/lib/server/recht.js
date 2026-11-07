// Gesetz (KiBG) und Verordnung (KiBV) als HTML für die Seite «Gesetzgebung».
// Die Texte stehen als Markdown in src/lib/recht/; jeder Artikel, Absatz und
// Buchstabe hat dort eine Sprungmarke (z. B. kibg-art-9-abs-2).

import { Marked } from 'marked';
import markedFootnote from 'marked-footnote';
import kibg from '#lib/recht/kibg.md?raw';
import kibv from '#lib/recht/kibv.md?raw';

// Eigene Fussnoten-Namen je Erlass, damit sich die Sprungmarken nicht
// überschneiden, wenn beide Texte auf einer Seite stehen.
function alsHtml(markdown, kuerzel) {
	return new Marked()
		.use(markedFootnote({ prefixId: `${kuerzel}-fn-`, description: 'Fussnoten' }))
		.parse(markdown.replace(/<!--[\s\S]*?-->/, ''));
}

export const KIBG_HTML = alsHtml(kibg, 'kibg');
export const KIBV_HTML = alsHtml(kibv, 'kibv');
