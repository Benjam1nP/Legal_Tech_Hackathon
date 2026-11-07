<script>
	import { texte } from '#lib/darstellung.js';
	import hintergrund from '#lib/assets/Hintergrund.webp';
</script>

<!-- Home: Bildband über die ganze Breite; Inhalt folgt noch -->
<section class="bildband">
	<img src={hintergrund} alt="" />
	<div class="inhalt">
		<h2>{texte.navigation.home}</h2>
	</div>
</section>

<style>
	/* Über die ganze Fensterbreite, direkt unter den Tabs */
	.bildband {
		position: relative;
		margin-top: -2rem;
		margin-inline: calc(50% - 50vw);
		height: clamp(18rem, 55vh, 32rem);
		overflow: hidden;
		background: var(--secondary);
	}

	img {
		position: absolute;
		inset: 0;
		width: 100%;
		height: 100%;
		object-fit: cover;
	}

	/* Leichter Verlauf unten, damit der Titel auf dem Foto lesbar bleibt */
	.bildband::after {
		content: '';
		position: absolute;
		inset: 0;
		background: linear-gradient(to top, rgb(10 14 19 / 0.55), transparent 55%);
	}

	.inhalt {
		position: absolute;
		z-index: 1;
		inset: auto 0 0;
		max-width: 46rem;
		margin: 0 auto;
		padding: 0 1rem 1.5rem;
	}

	h2 {
		margin: 0;
		font-size: var(--text-2xl);
		font-weight: 700;
		color: var(--card);
	}
</style>
