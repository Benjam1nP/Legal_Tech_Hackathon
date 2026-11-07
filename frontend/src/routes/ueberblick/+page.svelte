<script>
	// Tab «Überblick»: Ablauf aus Sicht der Eltern als Diagramm.
	// Jeder Schritt hat zwei Spuren (Swimlane): was die Eltern tun und was
	// Kita, Gemeinde oder Kanton erledigen. Texte in ablauf.de.json.
	import t from '#lib/ablauf.de.json';
	import Quelle from '#lib/Quelle.svelte';
</script>

<h2 class="titel">{t.titel}</h2>
<p class="einleitung">{t.einleitung}</p>

<!-- Übersicht: alle Schritte auf einen Blick, als Sprungmarken -->
<nav class="uebersicht" aria-label="Schritte">
	{#each t.schritte as s (s.nr)}
		<a href="#schritt-{s.nr}">
			<span class="nr figur">{s.nr}</span>
			<span>{s.titel}</span>
		</a>
	{/each}
</nav>

<ol class="ablauf">
	{#each t.schritte as s (s.nr)}
		<li id="schritt-{s.nr}">
			<span class="knoten figur" aria-hidden="true">{s.nr}</span>

			<section>
				<h3>{s.titel}</h3>
				<p class="kurz">{s.kurz}</p>

				{#if s.pruefung}
					<ul class="pruefung">
						{#each s.pruefung as p (p.text)}
							<li>{p.text} <Quelle verweise={p.quelle} /></li>
						{/each}
					</ul>

					<!-- Weiche: alles erfüllt oder nicht -->
					<div class="weiche">
						<div class="pfad ja">
							<p class="label">Alles erfüllt</p>
							<p>{s.weiche.ja}</p>
						</div>
						<div class="pfad nein">
							<p class="label">Nicht alles erfüllt</p>
							<p>{s.weiche.nein} <Quelle verweise={s.weiche.quelle} /></p>
						</div>
					</div>
				{/if}

				{#if s.sie || s.andere}
					<div class="spuren">
						{#if s.sie}
							<div class="spur sie">
								<p class="label">{t.spalten.sie}</p>
								<ul>
									{#each s.sie as p (p.text)}
										<li>{p.text} <Quelle verweise={p.quelle} /></li>
									{/each}
								</ul>
							</div>
						{/if}
						{#if s.andere}
							<div class="spur andere">
								<p class="label">{t.spalten.andere}</p>
								<ul>
									{#each s.andere as p (p.text)}
										<li><strong>{p.wer}</strong> {p.text} <Quelle verweise={p.quelle} /></li>
									{/each}
								</ul>
							</div>
						{/if}
					</div>
				{/if}

				{#if s.frist}
					<!-- Zeitstrahl der 30-Tage-Frist -->
					<div class="frist">
						<p class="label">{s.frist.titel}</p>
						<div class="strahl" aria-hidden="true">
							<span class="innert figur">Tag 1–30</span>
							<span class="spaeter figur">ab Tag 31</span>
						</div>
						<p class="marken figur" aria-hidden="true">↑ {s.frist.start}</p>
						<ul>
							<li class="gut">{s.frist.innert}</li>
							<li>{s.frist.spaeter}</li>
						</ul>
						<p class="klein">{s.frist.start_system} <Quelle verweise={s.frist.quelle} /></p>
					</div>
				{/if}

				{#if s.gut_zu_wissen}
					<details>
						<summary>Gut zu wissen</summary>
						<ul>
							{#each s.gut_zu_wissen as p (p.text)}
								<li>{p.text} <Quelle verweise={p.quelle} /></li>
							{/each}
						</ul>
					</details>
				{/if}

				{#if s.achtung}
					<p class="achtung">{s.achtung.text} <Quelle verweise={s.achtung.quelle} /></p>
				{/if}

				{#if s.zurueck_zu}
					<a class="zurueck" href="#schritt-{s.zurueck_zu}">
						Neues Gesuch: weiter bei Schritt {s.zurueck_zu}
					</a>
				{/if}
			</section>
		</li>
	{/each}
</ol>

<p class="vorbehalt">{t.vorbehalt}</p>

<style>
	.titel {
		margin: 0;
		font-size: var(--text-xl);
		line-height: 1.75rem;
		font-weight: 700;
		color: var(--gruen-wappen);
	}

	.einleitung {
		margin: 0.5rem 0 1.5rem;
		color: var(--muted-foreground);
	}

	p {
		margin: 0;
	}

	ul {
		margin: 0.5rem 0 0;
		padding-left: 1.1rem;
		font-size: var(--text-sm);
	}

	li + li {
		margin-top: 0.35rem;
	}

	/* Übersicht: sechs Schritte als Leiste */
	.uebersicht {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 1px;
		margin-bottom: 2rem;
		background: var(--border);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
		overflow: hidden;
	}

	.uebersicht a {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.6rem 0.75rem;
		background: var(--card);
		color: var(--foreground);
		font-size: var(--text-sm);
		font-weight: 500;
		line-height: 1.25rem;
		text-decoration: none;
		transition: background-color 100ms ease-out;
	}

	.uebersicht a:hover {
		background: var(--secondary);
	}

	.uebersicht a:focus-visible {
		outline: 3px solid var(--ring);
		outline-offset: -3px;
	}

	.nr {
		flex: none;
		display: grid;
		place-items: center;
		width: 1.5rem;
		height: 1.5rem;
		font-size: var(--text-xs);
		color: var(--primary);
		border: 1px solid var(--primary);
		border-radius: 50%;
	}

	/* Ablauf: Knoten links, verbunden durch eine Linie */
	.ablauf {
		margin: 0;
		padding: 0;
		list-style: none;
	}

	.ablauf > li {
		position: relative;
		display: grid;
		grid-template-columns: 2.25rem 1fr;
		gap: 0.75rem;
		padding-bottom: 1.25rem;
		scroll-margin-top: 1rem;
	}

	.ablauf > li + li {
		margin-top: 0;
	}

	/* Verbindungslinie zum nächsten Schritt */
	.ablauf > li:not(:last-child)::before {
		content: '';
		position: absolute;
		top: 2.25rem;
		bottom: 0;
		left: calc(1.125rem - 1px);
		width: 2px;
		background: color-mix(in oklch, var(--primary) 35%, var(--border));
	}

	.knoten {
		display: grid;
		place-items: center;
		width: 2.25rem;
		height: 2.25rem;
		font-weight: 500;
		color: var(--primary-foreground);
		background: var(--primary);
		border-radius: 50%;
	}

	section {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		min-width: 0;
		padding: 1.25rem;
		background: var(--card);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
	}

	h3 {
		margin: 0;
		font-size: var(--text-lg);
		font-weight: 600;
	}

	.kurz {
		color: var(--muted-foreground);
	}

	/* Prüfliste in Schritt 1: gleiche Punkte wie die übrigen Listen */
	.pruefung {
		margin: 0;
	}

	/* Weiche: zwei Ausgänge */
	.weiche,
	.spuren {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 0.75rem;
	}

	.pfad,
	.spur {
		padding: 0.75rem 0.9rem;
		font-size: var(--text-sm);
		border-radius: var(--radius-md);
	}

	.pfad .label,
	.spur .label {
		margin-bottom: 0.25rem;
	}

	.pfad.ja,
	.spur.sie {
		background: color-mix(in oklch, var(--primary) 6%, var(--card));
		border-left: 2px solid var(--primary);
	}

	.pfad.nein,
	.spur.andere {
		background: var(--secondary);
		border-left: 2px solid var(--input);
	}

	.spur ul {
		margin: 0;
	}

	/* Zeitstrahl der Frist */
	.frist {
		padding: 0.75rem 0.9rem;
		font-size: var(--text-sm);
		border: 1px solid var(--border);
		border-radius: var(--radius-md);
	}

	/* Zwei beschriftete Abschnitte: innert der Frist (grün) und danach */
	.strahl {
		display: flex;
		margin-top: 0.6rem;
		font-size: var(--text-xs);
		line-height: 1.5rem;
		border-radius: var(--radius-md);
		overflow: hidden;
	}

	.strahl span {
		flex: 1;
		padding: 0 0.6rem;
		white-space: nowrap;
	}

	.strahl .innert {
		color: var(--primary-foreground);
		background: var(--primary);
	}

	.strahl .spaeter {
		color: var(--muted-foreground);
		background: var(--secondary);
	}

	.marken {
		margin-top: 0.25rem;
		font-size: var(--text-xs);
		color: var(--muted-foreground);
	}

	.frist ul {
		list-style: none;
		padding: 0;
	}

	.frist li {
		position: relative;
		padding-left: 1.1rem;
	}

	.frist li::before {
		content: '';
		position: absolute;
		left: 0;
		top: 0.45rem;
		width: 0.6rem;
		height: 0.6rem;
		background: var(--border);
		border-radius: 50%;
	}

	.frist li.gut::before {
		background: var(--primary);
	}

	.klein {
		margin-top: 0.5rem;
		font-size: var(--text-xs);
		color: var(--muted-foreground);
	}

	details {
		border-top: 1px solid var(--border);
		padding-top: 0.75rem;
	}

	summary {
		cursor: pointer;
		font-size: var(--text-sm);
		font-weight: 500;
	}

	summary:hover {
		color: var(--primary);
	}

	summary:focus-visible {
		outline: 3px solid var(--ring);
		border-radius: var(--radius-md);
	}

	.achtung {
		padding: 0.75rem 0.9rem;
		font-size: var(--text-sm);
		background: color-mix(in oklch, var(--destructive) 6%, var(--card));
		border-left: 2px solid var(--destructive);
		border-radius: var(--radius-md);
	}

	.zurueck {
		align-self: flex-start;
		font-size: var(--text-sm);
		font-weight: 500;
		color: var(--primary);
	}

	.zurueck:focus-visible {
		outline: 3px solid var(--ring);
		border-radius: var(--radius-md);
	}

	.vorbehalt {
		margin-top: 1rem;
		padding: 0.9rem 1rem;
		font-size: var(--text-sm);
		color: var(--muted-foreground);
		background: var(--card);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
	}

	/* Handy: Spuren untereinander, Übersicht in zwei Spalten */
	@media (max-width: 40rem) {
		.uebersicht {
			grid-template-columns: 1fr 1fr;
		}

		.weiche,
		.spuren {
			grid-template-columns: 1fr;
		}

		.ablauf > li {
			grid-template-columns: 1.75rem 1fr;
			gap: 0.5rem;
		}

		.knoten {
			width: 1.75rem;
			height: 1.75rem;
			font-size: var(--text-sm);
		}

		.ablauf > li:not(:last-child)::before {
			top: 1.75rem;
			left: calc(0.875rem - 1px);
		}

		section {
			padding: 1rem;
		}
	}
</style>
