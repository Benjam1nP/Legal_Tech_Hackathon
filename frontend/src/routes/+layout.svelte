<script>
	let { children } = $props();
</script>

<svelte:head>
	<title>Kinderbetreuung: Beitrag berechnen</title>
</svelte:head>

<header>
	<div class="inhalt">
		<h1>Kinderbetreuung: Beitrag berechnen</h1>
		<p>Prototyp · Kanton St. Gallen · Verordnung im Entwurf</p>
	</div>
</header>

<main class="inhalt">
	{@render children()}
</main>

<style>
	/* Farben an einer Stelle. --gruen nähert das Grün des Kantonswappens an;
	   den offiziellen Farbcode hier einsetzen. */
	:global(:root) {
		--gruen: #009a49;
		--gruen-text: #00703a; /* dunkler, damit Text auf Weiss gut lesbar ist */
		--gruen-hell: #e8f5ee;
		--schwarz: #111111;
		--weiss: #ffffff;
		--grau: #595959;
		--grau-linie: #8c8c8c;
		--grau-hell: #f3f3f3;
		--fehler: #b3261e;
	}

	:global(*, *::before, *::after) {
		box-sizing: border-box;
	}

	:global(body) {
		margin: 0;
		background: var(--weiss);
		color: var(--schwarz);
		font-family: system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
		font-size: 1.0625rem;
		line-height: 1.5;
	}

	header {
		background: var(--gruen);
		color: var(--weiss);
		padding: 1.25rem 0;
	}

	header h1 {
		margin: 0;
		font-size: 1.6rem;
	}

	header p {
		margin: 0.25rem 0 0;
	}

	.inhalt {
		max-width: 52rem;
		margin: 0 auto;
		padding: 0 1rem;
	}

	main {
		padding-top: 1.5rem;
		padding-bottom: 3rem;
	}
</style>
