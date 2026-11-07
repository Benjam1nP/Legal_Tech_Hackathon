<script>
	// Balken-Chart als SVG (ohne Bibliothek) mit positiven und negativen Werten.
	// Positive Balken grün, negative rot; die Nulllinie ist hervorgehoben.
	let {
		titel,
		x = [],
		werte = [],
		markiertesX = null,
		xTitel = '',
		formatX = (wert) => String(wert),
		formatY = (wert) => String(wert)
	} = $props();

	const B = 640;
	const H = 260;
	const RAND = { links: 64, rechts: 16, oben: 16, unten: 44 };

	// «Runder» Schritt für die Achse (1, 2, 2.5, 5 × 10^n).
	function schritt(spanne) {
		const roh = Math.max(1, spanne) / 4;
		const basis = 10 ** Math.floor(Math.log10(roh));
		return [1, 2, 2.5, 5, 10].find((s) => s * basis >= roh) * basis;
	}

	let gueltig = $derived(werte.filter((w) => w !== null));
	let roh = $derived([Math.min(0, ...gueltig), Math.max(0, ...gueltig)]);
	let s = $derived(schritt(roh[1] - roh[0]));
	let unten = $derived(Math.floor(roh[0] / s) * s);
	let oben = $derived(Math.max(s, Math.ceil(roh[1] / s) * s));
	let spanne = $derived(oben - unten);
	let ticks = $derived(
		Array.from({ length: Math.round(spanne / s) + 1 }, (_, i) => unten + i * s)
	);

	let breite = $derived((B - RAND.links - RAND.rechts) / Math.max(1, x.length));
	const py = (wert) => RAND.oben + ((oben - wert) / spanne) * (H - RAND.oben - RAND.unten);
	const bx = (i) => RAND.links + i * breite;
</script>

<figure>
	<figcaption>{titel}</figcaption>
	<svg viewBox="0 0 {B} {H}" role="img" aria-label={titel}>
		{#each ticks as tick (tick)}
			<line x1={RAND.links} x2={B - RAND.rechts} y1={py(tick)} y2={py(tick)} class="raster" />
			<text x={RAND.links - 8} y={py(tick) + 4} class="achse" text-anchor="end">{formatY(tick)}</text>
		{/each}

		{#each x as wert, i (wert)}
			{@const w = werte[i]}
			{#if w !== null}
				<rect
					x={bx(i) + breite * 0.18}
					y={Math.min(py(w), py(0))}
					width={breite * 0.64}
					height={Math.max(1, Math.abs(py(w) - py(0)))}
					class={[w < 0 ? 'negativ' : 'positiv', wert === markiertesX && 'gewaehlt']}
				>
					<title>{formatX(wert)}: {formatY(w)}</title>
				</rect>
			{/if}
			<text x={bx(i) + breite / 2} y={H - RAND.unten + 18} class="achse" text-anchor="middle">
				{formatX(wert)}
			</text>
		{/each}
		<line x1={RAND.links} x2={B - RAND.rechts} y1={py(0)} y2={py(0)} class="null" />
		<text x={(B + RAND.links) / 2} y={H - 6} class="achsentitel" text-anchor="middle">{xTitel}</text>
	</svg>
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

	.null {
		stroke: var(--foreground);
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

	.positiv {
		fill: var(--gruen-wappen);
	}

	.negativ {
		fill: var(--destructive);
	}

	.gewaehlt {
		stroke: var(--foreground);
		stroke-width: 2;
	}
</style>
