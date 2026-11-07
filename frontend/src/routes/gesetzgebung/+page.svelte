<script>
	// Wortlaut von Gesetz und Verordnung. Links wie /gesetzgebung#kibg-art-9-abs-2
	// springen zum Absatz; dieser wird hervorgehoben. Die Verweise im Tab
	// «Überblick» führen hierher (src/lib/quellen.js).
	import { texte } from '#lib/darstellung.js';

	let { data } = $props();
	const t = texte.gesetzgebung;
</script>

<h2>{t.titel}</h2>
<p class="einleitung">{t.einleitung}</p>

<nav class="inhalt-nav" aria-label={t.inhalt}>
	<a href="#kibg">{t.kibg}</a>
	<a href="#kibv">{t.kibv}</a>
	<a class="pdf" href="/quellen/KiBG.pdf" target="_blank" rel="noopener">{t.pdf_kibg}</a>
	<a class="pdf" href="/quellen/KiBV-Entwurf.pdf" target="_blank" rel="noopener">{t.pdf_kibv}</a>
</nav>

<article id="kibg" class="erlass">
	<!-- Eigener Inhalt aus src/lib/recht/kibg.md -->
	{@html data.kibg}
</article>

<article id="kibv" class="erlass">
	<p class="quelle entwurf">{t.kibv_quelle}</p>
	<!-- Eigener Inhalt aus src/lib/recht/kibv.md -->
	{@html data.kibv}
</article>

<style>
	h2 {
		margin: 0;
		font-size: var(--text-xl);
		line-height: 1.75rem;
		font-weight: 700;
		color: var(--gruen-wappen);
	}

	.einleitung {
		margin: 0.5rem 0 1rem;
		color: var(--muted-foreground);
	}

	.inhalt-nav {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 1.5rem;
	}

	.inhalt-nav a {
		padding: 0.375rem 0.75rem;
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		background: var(--card);
		color: var(--foreground);
		font-size: var(--text-sm);
		font-weight: 500;
		text-decoration: none;
	}

	.inhalt-nav a:hover {
		border-color: var(--muted-foreground);
	}

	.inhalt-nav a.pdf {
		border-color: transparent;
		background: none;
		color: var(--muted-foreground);
		text-decoration: underline;
		text-underline-offset: 2px;
	}

	.inhalt-nav a.pdf:hover {
		color: var(--primary);
	}

	.erlass {
		padding: 1.25rem 1.5rem;
		margin-bottom: 1.5rem;
		background: var(--card);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
		scroll-margin-top: 1rem;
	}

	.quelle {
		margin: 0 0 0.5rem;
		font-size: var(--text-sm);
		color: var(--muted-foreground);
	}

	.quelle.entwurf {
		padding: 0.5rem 0.75rem;
		border-left: 3px solid var(--gruen-wappen);
		background: color-mix(in oklch, var(--gruen-wappen) 8%, var(--card));
		color: var(--foreground);
	}

	/* Gliederung: Titel, Ziffer, Abschnitt, Artikel */
	.erlass :global(h1) {
		margin: 0.5rem 0 1rem;
		font-size: var(--text-lg);
		line-height: 1.5rem;
		font-weight: 700;
	}

	.erlass :global(h2) {
		margin: 2rem 0 0.5rem;
		font-size: var(--text-base);
		font-weight: 700;
		color: var(--muted-foreground);
	}

	.erlass :global(h3) {
		margin: 2rem 0 0.25rem;
		padding-bottom: 0.375rem;
		border-bottom: 1px solid var(--border);
		font-size: var(--text-base);
		font-weight: 700;
		color: var(--gruen-wappen);
	}

	.erlass :global(h4) {
		margin: 1.5rem 0 0.5rem;
		font-size: var(--text-base);
		font-weight: 600;
	}

	.erlass :global(h4 + p > em) {
		color: var(--muted-foreground);
	}

	.erlass :global(p),
	.erlass :global(li) {
		line-height: 1.6;
	}

	.erlass :global(p) {
		margin: 0.5rem 0;
	}

	/* Absatznummer hochgestellt, wie im Erlass */
	.erlass :global(sup) {
		font-size: 0.7em;
		color: var(--muted-foreground);
	}

	/* Buchstaben und Ziffern ohne Aufzählungszeichen, eingerückt */
	.erlass :global(ul) {
		list-style: none;
		margin: 0.25rem 0 0.5rem;
		padding-left: 1.25rem;
	}

	.erlass :global(li) {
		margin: 0.25rem 0;
	}

	.erlass :global(table) {
		border-collapse: collapse;
		margin: 0.75rem 0;
		font-size: var(--text-sm);
	}

	.erlass :global(th),
	.erlass :global(td) {
		padding: 0.375rem 0.75rem;
		border: 1px solid var(--border);
		text-align: left;
		vertical-align: top;
	}

	.erlass :global(.footnotes) {
		margin-top: 2rem;
		font-size: var(--text-sm);
		color: var(--muted-foreground);
	}

	/* Sprungmarken: Platz oben lassen und den Zielabsatz hervorheben */
	.erlass :global(a[id]) {
		scroll-margin-top: 5rem;
	}

	.erlass :global(:is(p, li, h4):has(> a:target)) {
		margin-left: -0.5rem;
		padding: 0.25rem 0.5rem;
		border-radius: var(--radius-md);
		background: color-mix(in oklch, var(--gruen-wappen) 14%, var(--card));
	}

	/* Ein Absatz mit Buchstaben: die Liste darunter gehört dazu */
	.erlass :global(p:has(> a:target)) {
		margin-bottom: 0;
	}

	.erlass :global(p:has(> a:target) + ul) {
		margin: 0 0 0 -0.5rem;
		/* Abstand oben innen, damit der Rand der ersten Zeile nicht hinausragt */
		padding: 0.0625rem 0.5rem 0.25rem 1.75rem;
		border-radius: 0 0 var(--radius-md) var(--radius-md);
		background: color-mix(in oklch, var(--gruen-wappen) 14%, var(--card));
	}

	.erlass :global(p:has(> a:target):has(+ ul)) {
		border-radius: var(--radius-md) var(--radius-md) 0 0;
	}

	@media (max-width: 40rem) {
		.erlass {
			padding: 1rem;
		}

		.erlass :global(table) {
			display: block;
			overflow-x: auto;
		}
	}
</style>
