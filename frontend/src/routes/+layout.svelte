<script>
	import '../app.css';
	import { page } from '$app/state';
	import { texte } from '#lib/darstellung.js';

	let { children } = $props();

	const TABS = [
		{ href: '/', text: texte.navigation.home },
		{ href: '/rechner', text: texte.navigation.rechner },
		{ href: '/dashboard', text: texte.navigation.dashboard },
		{ href: '/ueberblick', text: texte.navigation.ueberblick },
		{ href: '/gesetzgebung', text: texte.navigation.gesetzgebung }
	];
</script>

<svelte:head>
	<title>Kinderbetreuung: Beitrag berechnen</title>
</svelte:head>

<header>
	<div class="inhalt">
		<p class="label">Prototyp Kanton St. Gallen</p>
		<h1>Kinderbetreuung: Beitrag berechnen</h1>
		<nav aria-label="Hauptnavigation">
			{#each TABS as tab (tab.href)}
				<a
					href={tab.href}
					aria-current={page.url.pathname === tab.href ? 'page' : undefined}
				>
					{tab.text}
				</a>
			{/each}
		</nav>
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
		padding-top: 1.5rem;
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

	/* Tabs: aktiver Tab mit grüner Linie unten, wie die Navigation im Style-Kit */
	nav {
		display: flex;
		gap: 0.25rem;
		margin-top: 1rem;
		/* Auf schmalen Bildschirmen scrollen die Tabs, nicht die ganze Seite */
		overflow-x: auto;
		scrollbar-width: none;
	}

	nav a {
		flex-shrink: 0;
		white-space: nowrap;
		padding: 0.5rem 0.75rem;
		border-bottom: 2px solid transparent;
		color: var(--muted-foreground);
		font-size: var(--text-sm);
		font-weight: 500;
		text-decoration: none;
		transition:
			color 100ms ease-out,
			border-color 100ms ease-out;
	}

	nav a:hover {
		color: var(--foreground);
	}

	nav a[aria-current='page'] {
		color: var(--foreground);
		border-bottom-color: var(--primary);
	}

	nav a:focus-visible {
		outline: 3px solid var(--ring);
		border-radius: var(--radius-md);
	}

	.inhalt {
		width: 100%;
		max-width: 46rem;
		margin: 0 auto;
		padding: 0 1rem;
	}

	/* main.inhalt, damit .inhalt (Innenabstand nur seitlich) den Abstand oben
	   und unten nicht überschreibt */
	main.inhalt {
		flex: 1 0 auto;
		padding-top: 2rem;
		padding-bottom: 4rem;
	}
</style>
