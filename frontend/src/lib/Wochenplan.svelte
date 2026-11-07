<script>
	// Wochenplan mit Halbtagen (Montag bis Freitag, Vormittag und Nachmittag).
	// Zeilen zum Anklicken (wer arbeitet, wer hilft, Schulzeit) und berechnete
	// Zeilen (wann Betreuung nötig ist). Jeder Halbtag ist ein Knopf, damit
	// Tastatur und Screenreader funktionieren.
	import { TAGE } from '#lib/vergleich.js';

	let { zeilen = [], texte, umschalten = () => {}, titel = '' } = $props();
	const HALB = [0, 1];
</script>

<div class="rahmen">
	<table aria-label={titel}>
		<thead>
			<tr>
				<th scope="col" class="leer"></th>
				{#each TAGE as tag (tag)}
					<th scope="colgroup" colspan="2">{tag}</th>
				{/each}
			</tr>
			<tr class="unterkopf">
				<th scope="col" class="leer"></th>
				{#each TAGE as tag (tag)}
					{#each HALB as h (h)}
						<th scope="col">{h === 0 ? texte.vormittag_kurz : texte.nachmittag_kurz}</th>
					{/each}
				{/each}
			</tr>
		</thead>
		<tbody>
			{#each zeilen as zeile (zeile.schluessel)}
				<!-- Auf schmalen Bildschirmen steht der Titel über der Zeile -->
				<tr class={['titel-mobil', zeile.art]} aria-hidden="true">
					<td colspan="10">
						{zeile.titel}
						{#if zeile.untertitel}<span class="untertitel">{zeile.untertitel}</span>{/if}
					</td>
				</tr>
				<tr class={['zeile', zeile.art]}>
					<th scope="row">
						{zeile.titel}
						{#if zeile.untertitel}<span class="untertitel">{zeile.untertitel}</span>{/if}
					</th>
					{#each zeile.plan as an, i (i)}
						<td class={[i % 2 === 1 && 'nachmittag']}>
							{#if zeile.editierbar}
								<button
									type="button"
									class={['feld', an && 'an', zeile.neu?.[i] && 'neu']}
									aria-pressed={an}
									aria-label="{zeile.titel}, {TAGE[Math.floor(i / 2)]} {i % 2 === 0
										? texte.vormittag
										: texte.nachmittag}"
									onclick={() => umschalten(zeile.schluessel, i)}
								></button>
							{:else}
								<span
									class={['feld', an && 'an', zeile.neu?.[i] && 'neu']}
									title="{TAGE[Math.floor(i / 2)]} {i % 2 === 0 ? texte.vormittag : texte.nachmittag}"
								></span>
							{/if}
						</td>
					{/each}
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	.rahmen {
		overflow-x: auto;
		margin-top: 0.75rem;
	}

	table {
		border-collapse: separate;
		border-spacing: 0;
		font-size: var(--text-sm);
	}

	th {
		font-weight: 500;
		color: var(--muted-foreground);
		text-align: center;
		padding: 0.25rem 0.125rem;
		white-space: nowrap;
	}

	tbody th {
		text-align: left;
		color: var(--foreground);
		padding-right: 0.75rem;
		min-width: 9rem;
	}

	.untertitel {
		display: block;
		font-size: var(--text-xs);
		color: var(--muted-foreground);
		font-weight: 400;
	}

	.unterkopf th {
		font-size: var(--text-xs);
		font-weight: 400;
	}

	td {
		padding: 0.1875rem 0.0625rem;
		text-align: center;
	}

	/* kleiner Abstand zwischen den Tagen */
	td.nachmittag {
		padding-right: 0.5rem;
	}

	.zeile.betreuung th,
	.titel-mobil.betreuung td {
		color: var(--primary);
	}

	.titel-mobil {
		display: none;
	}

	.titel-mobil td {
		text-align: left;
		padding-top: 0.5rem;
		font-weight: 500;
	}


	.feld {
		display: block;
		width: 1.75rem;
		height: 1.75rem;
		border: 1px solid var(--input);
		border-radius: var(--radius-md);
		background: var(--card);
		padding: 0;
	}

	button.feld {
		cursor: pointer;
		transition: background-color 100ms ease-out;
	}

	button.feld:hover {
		border-color: var(--muted-foreground);
	}

	button.feld:focus-visible {
		outline: 3px solid var(--ring);
		outline-offset: 1px;
	}

	.arbeit .feld.an {
		background: var(--muted-foreground);
		border-color: var(--muted-foreground);
	}

	.hilfe .feld.an {
		background: color-mix(in oklch, var(--primary) 30%, var(--card));
		border-color: color-mix(in oklch, var(--primary) 50%, var(--card));
	}

	.schule .feld.an {
		background: var(--secondary);
		border-color: var(--muted-foreground);
		border-style: dashed;
	}

	.betreuung .feld {
		border-style: dotted;
	}

	.betreuung .feld.an {
		background: var(--gruen-wappen);
		border: 1px solid var(--gruen-wappen);
	}

	.feld.neu {
		box-shadow: 0 0 0 2px var(--card), 0 0 0 4px var(--foreground);
	}

	@media (max-width: 40rem) {
		.titel-mobil {
			display: table-row;
		}

		tbody th,
		thead .leer {
			display: none;
		}

		.feld {
			width: 1.5rem;
			height: 1.5rem;
		}

		td.nachmittag {
			padding-right: 0.25rem;
		}

		.unterkopf th {
			padding: 0.125rem 0;
			font-size: 0.6875rem;
		}
	}
</style>
