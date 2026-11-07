<script>
	import hintergrund from '#lib/assets/Hintergrund.webp';
</script>

<!-- Home: Foto über den ganzen Bildschirm unter den Tabs; Inhalt folgt noch -->
<div class="bild">
	<img src={hintergrund} alt="" />
</div>

<style>
	/* Auf Home füllt das Foto den ganzen Inhaltsbereich, ohne Abstände */
	:global(main:has(> .bild)) {
		display: flex;
		flex-direction: column;
	}

	/* Die negativen Ränder heben die Abstände des Inhaltsbereichs (oben 2rem,
	   unten 4rem, seitlich) auf, damit das Foto bis an alle Ränder reicht. */
	.bild {
		position: relative;
		flex: 1;
		min-height: 18rem;
		margin-top: -2rem;
		margin-bottom: -4rem;
		margin-inline: calc(50% - 50vw);
		background: var(--secondary);
	}

	img {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: cover;
	}
</style>
