<script>
	// Linien-Chart als SVG (ohne Bibliothek): eine Linie je Serie über einer
	// gemeinsamen x-Achse. Bereiche ohne Anspruch werden grau hinterlegt.
	let {
		titel,
		x = [],
		serien = [],
		bereiche = [],
		markiertesX = null,
		xTitel = '',
		yTitel = '',
		formatX = (wert) => String(wert),
		formatY = (wert) => String(wert)
	} = $props();

	const B = 640;
	const H = 280;
	const RAND = { links: 64, rechts: 16, oben: 16, unten: 44 };

	// «Runder» Schritt für die Achse (1, 2, 2.5, 5 × 10^n).
	function schritt(spanne) {
		const roh = Math.max(1, spanne) / 4;
		const basis = 10 ** Math.floor(Math.log10(roh));
		return [1, 2, 2.5, 5, 10].find((s) => s * basis >= roh) * basis;
	}

	let xMin = $derived(Math.min(...x));
	let xMax = $derived(Math.max(...x));
	let roh = $derived(Math.max(1, ...serien.flatMap((s) => s.werte.filter((w) => w !== null))));
	let s = $derived(schritt(roh));
	let yMax = $derived(Math.ceil(roh / s) * s);
	let ticks = $derived(Array.from({ length: Math.round(yMax / s) + 1 }, (_, i) => i * s));

	const px = (wert) =>
		RAND.links + ((wert - xMin) / Math.max(1, xMax - xMin)) * (B - RAND.links - RAND.rechts);
	const py = (wert) => H - RAND.unten - (wert / yMax) * (H - RAND.oben - RAND.unten);

	function pfad(werte) {
		return werte
			.map((w, i) => (w === null ? null : `${px(x[i]).toFixed(1)},${py(w).toFixed(1)}`))
			.filter(Boolean)
			.map((punkt, i) => (i === 0 ? `M${punkt}` : `L${punkt}`))
			.join(' ');
	}
</script>

<figure>
	<figcaption>{titel}</figcaption>
	<svg viewBox="0 0 {B} {H}" role="img" aria-label={titel}>
		{#each bereiche as bereich (bereich.text)}
			<rect
				x={px(bereich.von)}
				y={RAND.oben}
				width={Math.max(0, px(bereich.bis) - px(bereich.von))}
				height={H - RAND.oben - RAND.unten}
				class="bereich"
			>
				<title>{bereich.text}</title>
			</rect>
		{/each}

		{#each ticks as tick (tick)}
			<line x1={RAND.links} x2={B - RAND.rechts} y1={py(tick)} y2={py(tick)} class="raster" />
			<text x={RAND.links - 8} y={py(tick) + 4} class="achse" text-anchor="end">{formatY(tick)}</text>
		{/each}
		{#each x as wert (wert)}
			<text x={px(wert)} y={H - RAND.unten + 18} class="achse" text-anchor="middle">
				{formatX(wert)}
			</text>
		{/each}
		<text x={(B + RAND.links) / 2} y={H - 6} class="achsentitel" text-anchor="middle">{xTitel}</text>
		<text
			x={14}
			y={(H - RAND.unten) / 2}
			class="achsentitel"
			text-anchor="middle"
			transform="rotate(-90 14 {(H - RAND.unten) / 2})">{yTitel}</text
		>

		{#if markiertesX !== null}
			<line
				x1={px(markiertesX)}
				x2={px(markiertesX)}
				y1={RAND.oben}
				y2={H - RAND.unten}
				class="markierung"
			/>
		{/if}

		{#each serien as serie (serie.name)}
			<path d={pfad(serie.werte)} fill="none" stroke={serie.farbe} stroke-width="2.5" stroke-dasharray={serie.strich ?? ''} />
			{#each serie.werte as wert, i (i)}
				{#if wert !== null}
					<circle cx={px(x[i])} cy={py(wert)} r="3.5" fill={serie.farbe}>
						<title>{serie.name}, {formatX(x[i])}: {formatY(wert)}</title>
					</circle>
				{/if}
			{/each}
		{/each}
	</svg>
	<ul class="legende">
		{#each serien as serie (serie.name)}
			<li>
				<svg width="24" height="10" aria-hidden="true">
					<line x1="0" x2="24" y1="5" y2="5" stroke={serie.farbe} stroke-width="2.5" stroke-dasharray={serie.strich ?? ''} />
				</svg>
				{serie.name}
			</li>
		{/each}
		{#each bereiche as bereich (bereich.text)}
			<li><span class="feld-grau" aria-hidden="true"></span>{bereich.text}</li>
		{/each}
	</ul>
</figure>

<style>
	figure {
		margin: 0;
	}

	figcaption {
		font-size: var(--text-sm);
		font-weight: 600;
		margin-bottom: 0.5rem;
	}

	svg {
		display: block;
		width: 100%;
		height: auto;
	}

	.raster {
		stroke: var(--border);
		stroke-width: 1;
	}

	.achse {
		font-family: var(--font-mono);
		font-size: 12px;
		fill: var(--muted-foreground);
	}

	.achsentitel {
		font-size: 12px;
		fill: var(--muted-foreground);
	}

	.bereich {
		fill: var(--secondary);
	}

	.markierung {
		stroke: var(--foreground);
		stroke-width: 1;
		stroke-dasharray: 3 3;
	}

	.legende {
		display: flex;
		flex-wrap: wrap;
		gap: 0.25rem 1rem;
		margin: 0.5rem 0 0;
		padding: 0;
		list-style: none;
		font-size: var(--text-sm);
		color: var(--muted-foreground);
	}

	.legende li {
		display: inline-flex;
		align-items: center;
		gap: 0.375rem;
	}

	.legende svg {
		flex: none;
		width: 24px;
	}

	.feld-grau {
		display: inline-block;
		width: 14px;
		height: 10px;
		background: var(--secondary);
		border: 1px solid var(--border);
	}
</style>
