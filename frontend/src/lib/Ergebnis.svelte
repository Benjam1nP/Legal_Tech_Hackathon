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
		<h3>{bezeichnung}: voraussichtlicher Beitrag</h3>
		<p class="betrag">
			Fr. {einsetzen('{kibg_beitrag_total}', werte)} <span>pro Monat</span>
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
					<strong>{zeile.erfuellt ? 'Erfüllt' : 'Nicht erfüllt'}:</strong>
					{einsetzen(zeile.text, werte)}
					<span class="artikel">{zeile.artikel}</span>
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
	.ergebnis {
		border-left: 6px solid var(--grau-linie);
		background: var(--grau-hell);
		padding: 1rem 1.25rem;
		margin: 1.25rem 0;
	}

	.ergebnis.positiv {
		border-left-color: var(--gruen);
		background: var(--weiss);
		box-shadow: inset 0 0 0 1px var(--grau-linie);
	}

	h3 {
		margin: 0 0 0.5rem;
		font-size: 1.15rem;
	}

	.betrag {
		margin: 0.25rem 0 0.75rem;
		font-size: 2.2rem;
		font-weight: 700;
		color: var(--gruen-text);
	}

	.betrag span {
		font-size: 1rem;
		font-weight: 400;
		color: var(--schwarz);
	}

	details {
		border-top: 1px solid var(--grau-linie);
		padding: 0.6rem 0;
	}

	summary {
		cursor: pointer;
		font-weight: 600;
	}

	summary:focus-visible {
		outline: 3px solid var(--gruen);
	}

	li {
		margin: 0.5rem 0;
	}

	.voraussetzungen {
		list-style: none;
		padding-left: 0;
	}

	.voraussetzungen li {
		border-left: 4px solid var(--gruen);
		padding-left: 0.6rem;
	}

	.voraussetzungen li.nein {
		border-left-color: var(--fehler);
	}

	.artikel {
		display: block;
		color: var(--grau);
		font-size: 0.9rem;
	}
</style>
