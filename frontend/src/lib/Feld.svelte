<script>
	// Eingabefeld für Zahlen, Daten und Monate. Der Info-Text erscheint, sobald
	// man im Feld ist.
	let {
		id,
		label,
		wert = $bindable(),
		typ = 'number',
		hilfe = '',
		fehler = '',
		einheit = '',
		min = undefined,
		max = undefined,
		step = undefined
	} = $props();
</script>

<div class={['feld', fehler && 'mit-fehler']}>
	<label for={id}>{label}</label>
	<div class="eingabe">
		<input
			{id}
			type={typ}
			{min}
			{max}
			{step}
			inputmode={typ === 'number' ? 'decimal' : undefined}
			bind:value={wert}
			aria-invalid={fehler ? 'true' : undefined}
			aria-describedby={hilfe ? `${id}-hilfe` : undefined}
		/>
		{#if einheit}<span class="einheit">{einheit}</span>{/if}
	</div>
	{#if hilfe}
		<p class="hilfe" id="{id}-hilfe">{hilfe}</p>
	{/if}
	{#if fehler}
		<p class="meldung">{fehler}</p>
	{/if}
</div>

<style>
	.feld {
		position: relative;
		margin: 1rem 0;
	}

	label {
		display: block;
		font-weight: 600;
		margin-bottom: 0.3rem;
	}

	.eingabe {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	input {
		font: inherit;
		padding: 0.5rem 0.6rem;
		border: 1px solid var(--grau-linie);
		border-radius: 0;
		background: var(--weiss);
		color: var(--schwarz);
		width: 14rem;
		max-width: 100%;
	}

	input:focus {
		outline: 3px solid var(--gruen);
		outline-offset: 1px;
		border-color: var(--schwarz);
	}

	.einheit {
		color: var(--grau);
	}

	/* Info-Text nur anzeigen, solange man im Feld ist. Er schwebt über dem
	   Inhalt darunter, damit nichts verrutscht, wenn man ins nächste Feld klickt. */
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

	.feld:focus-within .hilfe {
		display: block;
	}

	.mit-fehler input {
		border: 2px solid var(--fehler);
	}

	.meldung {
		margin: 0.3rem 0 0;
		color: var(--fehler);
		font-size: 0.95rem;
	}
</style>
