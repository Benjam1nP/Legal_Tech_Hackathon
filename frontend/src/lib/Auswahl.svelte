<script>
	// Auswahlfrage mit grossen Knöpfen. Technisch Radio-Buttons, damit Tastatur
	// und Screenreader wie gewohnt funktionieren; der gewählte Knopf ist grün.
	let { name, frage, optionen, wert = $bindable(), hilfe = '', fehler = '' } = $props();
</script>

<fieldset class={['auswahl', fehler && 'mit-fehler']}>
	<legend>{frage}</legend>
	<div class="knoepfe">
		{#each optionen as option (option.wert)}
			<label class={['knopf', wert === option.wert && 'gewaehlt']}>
				<input type="radio" {name} value={option.wert} bind:group={wert} />
				{option.text}
			</label>
		{/each}
	</div>
	{#if hilfe}
		<p class="hilfe">{hilfe}</p>
	{/if}
	{#if fehler}
		<p class="meldung">{fehler}</p>
	{/if}
</fieldset>

<style>
	.auswahl {
		position: relative;
		border: 0;
		margin: 1.25rem 0;
		padding: 0;
		min-width: 0;
	}

	legend {
		font-size: var(--text-sm);
		font-weight: 500;
		margin-bottom: 0.375rem;
		padding: 0;
	}

	.knoepfe {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.knopf {
		position: relative;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		min-height: 2.25rem;
		min-width: 5rem;
		padding: 0.375rem 0.875rem;
		border: 1px solid var(--input);
		border-radius: var(--radius-md);
		background: var(--card);
		font-size: var(--text-sm);
		cursor: pointer;
		transition:
			background-color 100ms ease-out,
			border-color 100ms ease-out;
	}

	.knopf:hover {
		background: var(--secondary);
	}

	/* Gewählt: Akzentfarbe nur als Rand und leichte Fläche (Style-Kit) */
	.knopf.gewaehlt {
		border-color: var(--primary);
		background: color-mix(in oklch, var(--primary) 8%, var(--card));
		color: var(--primary);
		font-weight: 600;
		box-shadow: inset 0 0 0 1px var(--primary);
	}

	/* Radio-Kreis ausblenden, aber für Tastatur und Screenreader behalten. */
	input {
		position: absolute;
		opacity: 0;
		width: 1px;
		height: 1px;
	}

	.knopf:focus-within {
		outline: 3px solid var(--ring);
		outline-offset: 1px;
	}

	/* Wie bei den Eingabefeldern: Info-Text erscheint bei der Auswahl und
	   schwebt über dem Inhalt darunter. */
	.hilfe {
		display: none;
		position: absolute;
		z-index: 10;
		left: 0;
		top: 100%;
		width: min(100%, 32rem);
		margin: 0.375rem 0 0;
		padding: 0.625rem 0.75rem;
		background: var(--card);
		border: 1px solid var(--border);
		border-left: 2px solid var(--primary);
		border-radius: var(--radius-md);
		box-shadow: 0 8px 24px rgb(10 14 19 / 0.08);
		color: var(--muted-foreground);
		font-size: var(--text-sm);
		line-height: 1.25rem;
		pointer-events: none; /* Klicks gehen durch zum Feld darunter */
	}

	.auswahl:focus-within .hilfe {
		display: block;
	}

	.mit-fehler .knopf:not(.gewaehlt) {
		border-color: var(--destructive);
	}

	.meldung {
		margin: 0.375rem 0 0;
		color: var(--destructive);
		font-size: var(--text-sm);
	}
</style>
