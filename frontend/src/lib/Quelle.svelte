<script>
	// Artikelverweise in Klammern hinter dem Satz, etwas kleiner als der Text.
	// Jeder Artikel ist ein Link auf die Stelle im Gesetz.
	import { quelle } from '#lib/quellen.js';

	let { verweise = [] } = $props();
</script>

{#if verweise.length}
	<span class="quellen"
		>({#each verweise.map(quelle) as q, i (q.text)}{#if i}{', '}{/if}{#if q.href}<a
					href={q.href}
					target="_blank"
					rel="noopener">{q.text}</a
				>{:else}{q.text}{/if}{/each})</span
	>
{/if}

<style>
	.quellen {
		font-size: 0.75rem;
		color: var(--muted-foreground);
	}

	a {
		color: inherit;
		text-decoration: underline;
		text-decoration-color: var(--border);
		text-underline-offset: 2px;
		transition:
			color 100ms ease-out,
			text-decoration-color 100ms ease-out;
	}

	a:hover {
		color: var(--primary);
		text-decoration-color: currentColor;
	}

	a:focus-visible {
		outline: 3px solid var(--ring);
		border-radius: 2px;
	}
</style>
