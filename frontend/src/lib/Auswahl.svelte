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
		margin: 1rem 0;
		padding: 0;
	}

	legend {
		font-weight: 600;
		margin-bottom: 0.4rem;
		padding: 0;
	}

	.knoepfe {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.knopf {
		position: relative;
		border: 1px solid var(--schwarz);
		padding: 0.55rem 1.1rem;
		cursor: pointer;
		background: var(--weiss);
		min-width: 5.5rem;
		text-align: center;
	}

	.knopf:hover {
		background: var(--gruen-hell);
	}

	.knopf.gewaehlt {
		background: var(--gruen);
		border-color: var(--gruen);
		color: var(--weiss);
		font-weight: 600;
	}

	/* Radio-Kreis ausblenden, aber für Tastatur und Screenreader behalten. */
	input {
		position: absolute;
		opacity: 0;
		width: 1px;
		height: 1px;
	}

	.knopf:focus-within {
		outline: 3px solid var(--schwarz);
		outline-offset: 2px;
	}

	/* Wie bei den Eingabefeldern: Info-Text erscheint bei der Auswahl und
	   schwebt über dem Inhalt darunter. */
	.hilfe {
		display: none;
		margin: 0.4rem 0 0;
		padding: 0.5rem 0.7rem;
		position: absolute;
		z-index: 10;
		left: 0;
		top: 100%;
		width: min(100%, 34rem);
		box-shadow: 0 2px 6px rgb(0 0 0 / 0.25);
		pointer-events: none; /* Klicks gehen durch zum Feld darunter */
		background: var(--gruen-hell);
		border-left: 4px solid var(--gruen);
		font-size: 0.95rem;
	}

	.auswahl:focus-within .hilfe {
		display: block;
	}

	.mit-fehler .knopf:not(.gewaehlt) {
		border: 2px solid var(--fehler);
	}

	.meldung {
		margin: 0.3rem 0 0;
		color: var(--fehler);
		font-size: 0.95rem;
	}
</style>
