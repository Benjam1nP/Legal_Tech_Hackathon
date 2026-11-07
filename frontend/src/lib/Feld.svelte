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
			class={[typ === 'number' && 'figur zahl']}
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
		margin: 1.25rem 0;
	}

	label {
		display: block;
		font-size: var(--text-sm);
		font-weight: 500;
		margin-bottom: 0.375rem;
	}

	.eingabe {
		display: flex;
		align-items: center;
		gap: 0.5rem;
	}

	input {
		font: inherit;
		height: 2.25rem;
		padding: 0 0.75rem;
		border: 1px solid var(--input);
		border-radius: var(--radius-md);
		background: var(--card);
		color: var(--foreground);
		width: 14rem;
		max-width: 100%;
		transition: border-color 100ms ease-out;
	}

	/* Zahlen rechtsbündig in Mono (Style-Kit), ohne Pfeile zum Hoch-/Runterzählen */
	input.zahl {
		text-align: right;
		font-family: var(--font-mono);
		font-variant-numeric: tabular-nums;
		appearance: textfield;
		-moz-appearance: textfield;
	}

	input.zahl::-webkit-inner-spin-button,
	input.zahl::-webkit-outer-spin-button {
		-webkit-appearance: none;
		margin: 0;
	}

	input:hover {
		border-color: var(--muted-foreground);
	}

	input:focus {
		outline: 3px solid var(--ring);
		outline-offset: 0;
		border-color: var(--primary);
	}

	.einheit {
		color: var(--muted-foreground);
		font-size: var(--text-sm);
	}

	/* Info-Text nur anzeigen, solange man im Feld ist. Er schwebt über dem
	   Inhalt darunter, damit nichts verrutscht, wenn man ins nächste Feld klickt. */
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

	.feld:focus-within .hilfe {
		display: block;
	}

	.mit-fehler input {
		border-color: var(--destructive);
	}

	.meldung {
		margin: 0.375rem 0 0;
		color: var(--destructive);
		font-size: var(--text-sm);
	}
</style>
