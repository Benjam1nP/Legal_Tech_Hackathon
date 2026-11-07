<script>
	import '../app.css';

	let { children } = $props();
</script>

<svelte:head>
	<title>Kinderbetreuung: Beitrag berechnen</title>
</svelte:head>

<header>
	<div class="inhalt">
		<p class="label">Prototyp · Kanton St. Gallen · Verordnung im Entwurf</p>
		<h1>Kinderbetreuung: Beitrag berechnen</h1>
	</div>
</header>

<main class="inhalt">
	{@render children()}
</main>

<style>
	header {
		background: var(--card);
		border-top: 4px solid var(--gruen-wappen);
		border-bottom: 1px solid var(--border);
		padding: 1.5rem 0 1.25rem;
	}

	header h1 {
		margin: 0.25rem 0 0;
		font-size: var(--text-2xl);
		line-height: 2.125rem;
		font-weight: 700;
	}

	.label {
		margin: 0;
	}

	.inhalt {
		max-width: 46rem;
		margin: 0 auto;
		padding: 0 1rem;
	}

	/* main.inhalt, damit .inhalt (Innenabstand nur seitlich) den Abstand oben
	   und unten nicht überschreibt */
	main.inhalt {
		padding-top: 2rem;
		padding-bottom: 4rem;
	}
</style>
