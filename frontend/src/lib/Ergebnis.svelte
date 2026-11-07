<script>
	// Ergebnis für ein Kind: Betrag gross, Details aufklappbar. Alle Texte aus
	// texte.de.json; welche erscheinen, entscheidet darstellung.js.
	import {
		texte,
		einsetzen,
		ergebnisArt,
		voraussetzungen,
		rechenweg,
		hinweise
	} from '#lib/darstellung.js';

	let { bezeichnung, kind, eingabe, haushalt, angaben, partnerEinkommenZaehlt } = $props();

	// Alle Werte, die in die Texte eingesetzt werden können.
	let werte = $derived({
		...kind,
		...haushalt,
		kind: bezeichnung,
		kibg_einrichtungstyp: eingabe.typ,
		betreuungsstunden: eingabe.stunden,
		kibg_betreuungskosten: eingabe.kosten
	});
	let art = $derived(ergebnisArt(kind));
	let ergebnis = $derived(texte.ergebnis[art]);
	let liste = $derived(voraussetzungen(kind, haushalt, angaben));
	let schritte = $derived(rechenweg(kind, eingabe));
	let tipps = $derived(hinweise(kind, haushalt, angaben, partnerEinkommenZaehlt));
	let alleErfuellt = $derived(liste.every((zeile) => zeile.erfuellt));
</script>

<article class={['ergebnis', art === 'anspruch' ? 'positiv' : 'neutral']}>
	{#if art === 'anspruch'}
		<!-- Der Titel aus texte.de.json enthält den Betrag; hier steht er gross. -->
		<h3 class="label">{bezeichnung} · voraussichtlicher Beitrag</h3>
		<p class="betrag">
			<span class="figur">Fr. {einsetzen('{kibg_beitrag_total}', werte)}</span>
			<span class="einheit">pro Monat</span>
		</p>
	{:else}
		<h3>{einsetzen(ergebnis.titel, werte)}</h3>
	{/if}
	<p>{einsetzen(ergebnis.text, werte)}</p>

	<details open={!alleErfuellt}>
		<summary>
			{texte.voraussetzungen.titel}
			({alleErfuellt ? 'alle erfüllt' : 'nicht alle erfüllt'})
		</summary>
		<ul class="voraussetzungen">
			{#each liste as zeile (zeile.artikel)}
				<li class={zeile.erfuellt ? 'ja' : 'nein'}>
					<span class={['status', zeile.erfuellt ? 'ja' : 'nein']}>
						{zeile.erfuellt ? '✓ Erfüllt' : '✕ Nicht erfüllt'}
					</span>
					<span>
						{einsetzen(zeile.text, werte)}
						<span class="artikel">{zeile.artikel}</span>
					</span>
				</li>
			{/each}
		</ul>
	</details>

	{#if art === 'anspruch'}
		<details>
			<summary>{einsetzen(texte.rechenweg.titel, werte)}</summary>
			<ol>
				{#each schritte as schritt (schritt.text)}
					<li>
						{einsetzen(schritt.text, werte)}
						<span class="artikel">{schritt.artikel}</span>
					</li>
				{/each}
			</ol>
		</details>
	{/if}

	{#if tipps.length}
		<details>
			<summary>{texte.hinweise.titel}</summary>
			<ul>
				{#each tipps as tipp (tipp.text)}
					<li>
						{einsetzen(tipp.text, werte)}
						<span class="artikel">{tipp.artikel}</span>
					</li>
				{/each}
			</ul>
		</details>
	{/if}
</article>

<style>
	/* Karte mit 2px-Akzentlinie links, wie die hervorgehobene Karte im Style-Kit */
	.ergebnis {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		margin: 1rem 0;
		padding: 1.25rem;
		background: var(--card);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
		animation: einblenden 200ms var(--ease);
	}

	.ergebnis.positiv {
		border-left: 2px solid var(--primary);
	}

	@keyframes einblenden {
		from {
			opacity: 0;
		}
	}

	h3 {
		margin: 0;
		font-size: var(--text-lg);
		font-weight: 600;
	}

	h3.label {
		font-size: var(--text-xs);
	}

	p {
		margin: 0;
	}

	.betrag {
		display: flex;
		align-items: baseline;
		gap: 0.5rem;
		font-size: var(--text-3xl);
		line-height: 2.5rem;
		font-weight: 500;
		color: var(--primary);
	}

	.betrag .einheit {
		font-size: var(--text-sm);
		color: var(--muted-foreground);
	}

	details {
		border-top: 1px solid var(--border);
		padding-top: 0.75rem;
	}

	summary {
		cursor: pointer;
		font-size: var(--text-sm);
		font-weight: 500;
	}

	summary:hover {
		color: var(--primary);
	}

	summary:focus-visible {
		outline: 3px solid var(--ring);
		border-radius: var(--radius-md);
	}

	ul,
	ol {
		margin: 0.5rem 0 0;
		padding-left: 1.25rem;
		font-size: var(--text-sm);
	}

	li {
		margin: 0.5rem 0;
	}

	.voraussetzungen {
		list-style: none;
		padding-left: 0;
	}

	.voraussetzungen li {
		display: grid;
		grid-template-columns: 7.5rem 1fr;
		gap: 0.75rem;
		align-items: start;
	}

	/* Neutrale Status-Badges: das Zeichen trägt die Bedeutung (Style-Kit) */
	.status {
		justify-self: start;
		padding: 0.0625rem 0.5rem;
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
		background: var(--secondary);
		font-size: var(--text-xs);
		font-weight: 500;
		white-space: nowrap;
	}

	.status.nein {
		color: var(--destructive);
	}

	.artikel {
		display: block;
		color: var(--muted-foreground);
		font-size: var(--text-xs);
	}
</style>
