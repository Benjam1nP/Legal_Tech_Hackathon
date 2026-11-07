<script>
	// Dashboard: Vergleich «Mehr arbeiten – welche Betreuung – was bleibt?».
	// Alle Beträge rechnet OpenFisca (Route /api/vergleich); hier stehen nur
	// Eingaben, der Vorschlag für die Betreuungstage und die Darstellung.
	import Auswahl from '#lib/Auswahl.svelte';
	import Feld from '#lib/Feld.svelte';
	import LinienChart from '#lib/LinienChart.svelte';
	import BalkenChart from '#lib/BalkenChart.svelte';
	import { texte, einsetzen } from '#lib/darstellung.js';
	import {
		FORMEN,
		VORGABE_PREIS,
		VORGABE_STUNDEN,
		formenFuer,
		stufenMit,
		vorschlagTage
	} from '#lib/vergleich.js';

	const t = texte.dashboard;
	const f = texte.formular;
	const KURZNAME = { kita: 'Kita', tagesfamilie: 'Tagesfamilie', schulergaenzend: 'Schulergänzend', keine: 'Keine' };
	const FARBE = {
		kita: 'var(--primary)',
		tagesfamilie: 'var(--foreground)',
		schulergaenzend: 'var(--muted-foreground)'
	};
	const STRICH = { kita: '', tagesfamilie: '6 4', schulergaenzend: '2 4' };
	const JA_NEIN = [
		{ wert: true, text: f.ja },
		{ wert: false, text: f.nein }
	];

	// Zahlen anzeigen: 1234.5 → 1'234.50 bzw. 1'235
	const tausender = (ganz) => ganz.replace(/\B(?=(\d{3})+(?!\d))/g, "'");
	const franken = (wert) => {
		const [ganz, rappen] = Math.abs(Number(wert)).toFixed(2).split('.');
		return `${Number(wert) < 0 ? '−' : ''}${tausender(ganz)}.${rappen}`;
	};
	const rund = (wert) => `${Number(wert) < 0 ? '−' : ''}${tausender(Math.abs(Math.round(Number(wert))).toString())}`;
	const prozent = (wert) => `${wert} %`;

	let naechsteKindNr = 1;
	const neuesKind = (werte = {}) => ({
		nr: naechsteKindNr++,
		geburtsdatum: '',
		eingeschult: null,
		form: null,
		preise: { ...VORGABE_PREIS },
		stunden: { ...VORGABE_STUNDEN },
		...werte
	});

	// Beispielwerte (Familie P1 aus challenge/szenarien.md), zum Anpassen.
	let monat = $state('2028-09');
	let anzahl = $state(2);
	let eltern = $state([
		{ pensum: 100, einkommen: 60000 },
		{ pensum: 40, einkommen: 37000 }
	]);
	let variiertWahl = $state(1);
	let lohn100 = $state(7000);
	let kinder = $state([neuesKind({ geburtsdatum: '2027-09-01', eingeschult: false, form: 'kita' })]);
	let vergleichKind = $state(0);
	// Eigene Betreuungstage pro Woche: { stufe: { kindIndex: tage } }
	let tageEigen = $state({});

	let ansicht = $state('kurz');
	let ziel = $state(60);
	let balkenForm = $state('beste');

	let ergebnis = $state(null);
	let berechnetMit = $state(null);
	let laeuft = $state(false);
	let versucht = $state(false);
	let serverFehler = $state([]);

	let paar = $derived(anzahl === 2);
	let variiert = $derived(paar ? variiertWahl : 0);
	let heute = $derived(Math.round(Number(eltern[variiert].pensum)));
	let andere = $derived(paar ? Number(eltern[1 - variiert].pensum) : 0);
	let stufen = $derived(stufenMit(heute));

	const vorschlag = (stufe) => vorschlagTage(stufe, andere, paar);
	const tageWert = (stufe, k) => tageEigen[stufe]?.[k] ?? vorschlag(stufe);
	function tageSetzen(stufe, k, wert) {
		tageEigen[stufe] = { ...(tageEigen[stufe] ?? {}), [k]: wert === '' ? undefined : Number(wert) };
	}

	let personenOptionen = $derived(
		eltern.slice(0, anzahl).map((_, i) => ({ wert: i, text: einsetzen(t.person, { nr: i + 1 }) }))
	);
	let kinderOptionen = $derived(
		kinder.map((_, i) => ({ wert: i, text: einsetzen(t.kind, { nr: i + 1 }) }))
	);
	const formOptionen = (kind) => [
		...formenFuer({ eingeschult: kind.eingeschult === true }).map((form) => ({
			wert: form,
			text: KURZNAME[form]
		})),
		{ wert: 'keine', text: t.form_heute.keine }
	];

	// Angaben für den Server: die ganze Tabelle der Betreuungstage mitschicken.
	let angaben = $derived({
		monat,
		variiert,
		lohn100: Number(lohn100),
		vergleichKind: Math.min(vergleichKind, kinder.length - 1),
		eltern: eltern.slice(0, anzahl).map((p) => ({ pensum: Number(p.pensum), einkommen: Number(p.einkommen) })),
		kinder: kinder.map((k) => ({
			geburtsdatum: k.geburtsdatum,
			eingeschult: k.eingeschult === true,
			form: k.form,
			preise: k.preise,
			stunden: k.stunden
		})),
		tage: Object.fromEntries(stufen.map((s) => [s, kinder.map((_, k) => tageWert(s, k))]))
	});
	let veraltet = $derived(ergebnis !== null && JSON.stringify(angaben) !== berechnetMit);

	// Pflichtangaben prüfen
	const leer = (wert) => wert === null || wert === undefined || wert === '';
	function monateAlt(geburtsdatum) {
		const [j, m, tag] = geburtsdatum.split('-').map(Number);
		const [mj, mm] = monat.split('-').map(Number);
		return (mj - j) * 12 + (mm - m) - (tag > 1 ? 1 : 0);
	}
	let meldungen = $derived.by(() => {
		const m = {};
		if (leer(monat)) m.monat = t.pflicht;
		if (leer(lohn100)) m.lohn100 = t.pflicht;
		eltern.slice(0, anzahl).forEach((p, i) => {
			if (leer(p.pensum)) m[`eltern.${i}.pensum`] = t.pflicht;
			if (leer(p.einkommen)) m[`eltern.${i}.einkommen`] = t.pflicht;
		});
		kinder.forEach((k, i) => {
			if (leer(k.geburtsdatum)) m[`kind.${i}.geburtsdatum`] = t.pflicht;
			if (k.eingeschult === null) m[`kind.${i}.eingeschult`] = t.pflicht;
			if (k.eingeschult === true && k.geburtsdatum && monateAlt(k.geburtsdatum) < 18) {
				m[`kind.${i}.eingeschult`] = t.kleinkind_eingeschult;
			}
			if (!k.form) m[`kind.${i}.form`] = t.pflicht;
			for (const form of formenFuer({ eingeschult: k.eingeschult === true })) {
				if (leer(k.preise[form])) m[`kind.${i}.preis.${form}`] = t.pflicht;
				if (leer(k.stunden[form])) m[`kind.${i}.stunden.${form}`] = t.pflicht;
			}
		});
		return m;
	});
	let fehler = $derived(versucht ? meldungen : {});

	async function vergleichen() {
		versucht = true;
		serverFehler = [];
		if (Object.keys(meldungen).length) return;
		laeuft = true;
		const gesendet = JSON.stringify(angaben);
		try {
			const antwort = await fetch('/api/vergleich', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: gesendet
			});
			const inhalt = await antwort.json();
			if (inhalt.fehler) {
				serverFehler = inhalt.fehler;
				ergebnis = null;
			} else {
				ergebnis = inhalt;
				berechnetMit = gesendet;
				if (!ergebnis.ergebnisse.some((e) => e.stufe === ziel)) ziel = Math.min(100, heute + 20);
			}
		} catch {
			serverFehler = [{ pfad: '', meldung: texte.fehler.allgemein }];
		} finally {
			laeuft = false;
		}
	}

	// Auswertung (nur Darstellung; alle Beträge stammen von OpenFisca)
	let formenErgebnis = $derived(
		ergebnis ? [...new Set(ergebnis.ergebnisse.map((e) => e.form))] : []
	);
	let stufenErgebnis = $derived(
		ergebnis ? [...new Set(ergebnis.ergebnisse.map((e) => e.stufe))].sort((a, b) => a - b) : []
	);
	const fall = (form, stufe, welche = ansicht) =>
		ergebnis?.ergebnisse.find((e) => e.ansicht === welche && e.form === form && e.stufe === stufe);
	const lohnHeute = () => Number(JSON.parse(berechnetMit).lohn100);
	function bleibt(form, stufe) {
		const e = fall(form, stufe);
		if (!e) return null;
		const mehrverdienst = (lohnHeute() * (stufe - ergebnis.heute)) / 100;
		return mehrverdienst - (e.restkosten - ergebnis.ausgangslage.restkosten);
	}
	function beste(stufe) {
		const faelle = formenErgebnis.map((form) => fall(form, stufe)).filter(Boolean);
		return faelle.reduce((a, b) => (b.restkosten < a.restkosten ? b : a), faelle[0]);
	}

	let serien = $derived(
		formenErgebnis.map((form) => ({
			name: KURZNAME[form],
			farbe: FARBE[form],
			strich: STRICH[form],
			werte: stufenErgebnis.map((s) => fall(form, s)?.restkosten ?? null)
		}))
	);
	// Bereiche ohne Anspruch nach den Ergebnissen von OpenFisca (lit. a / lit. b)
	let bereiche = $derived.by(() => {
		if (!ergebnis) return [];
		const liste = [];
		for (const s of stufenErgebnis) {
			const e = fall(formenErgebnis[0], s);
			if (!e || e.beschaeftigung) continue;
			const text = e.litA ? t.schwelle_b : t.schwelle_a;
			const letzter = liste.at(-1);
			if (letzter && letzter.text === text && letzter.bis >= s - 5) letzter.bis = Math.min(100, s + 5);
			else liste.push({ von: Math.max(0, s - 5), bis: Math.min(100, s + 5), text });
		}
		return liste;
	});
	let balken = $derived(
		stufenErgebnis.map((s) => (balkenForm === 'beste' ? bleibt(beste(s)?.form, s) : bleibt(balkenForm, s)))
	);
	let zielFall = $derived(ergebnis ? beste(ziel) : null);
	let mehrverdienst = $derived(ergebnis ? (lohnHeute() * (ziel - ergebnis.heute)) / 100 : 0);
	let mehrkosten = $derived(zielFall ? zielFall.restkosten - ergebnis.ausgangslage.restkosten : 0);
	let personName = $derived(einsetzen(t.person, { nr: variiert + 1 }));
</script>

<h2>{t.titel}</h2>
<p class="einleitung">{t.einleitung}</p>

<form
	novalidate
	onsubmit={(e) => {
		e.preventDefault();
		vergleichen();
	}}
>
	<section>
		<h2>{t.abschnitt_familie}</h2>
		<Feld id="monat" typ="month" label={t.monat.frage} hilfe={t.monat.hilfe} bind:wert={monat} fehler={fehler.monat} />
		<Auswahl
			name="anzahl"
			frage={t.anzahl_eltern.frage}
			optionen={[
				{ wert: 1, text: t.anzahl_eltern.eins },
				{ wert: 2, text: t.anzahl_eltern.zwei }
			]}
			bind:wert={anzahl}
		/>
		{#each eltern.slice(0, anzahl) as person, i (i)}
			<div class="unterblock">
				<h3>{einsetzen(t.person, { nr: i + 1 })}</h3>
				<div class="felder">
					<Feld
						id="pensum-{i}"
						label={t.pensum.frage}
						hilfe={t.pensum.hilfe}
						einheit="%"
						min="0"
						max="100"
						step="10"
						bind:wert={person.pensum}
						fehler={fehler[`eltern.${i}.pensum`]}
					/>
					<Feld
						id="einkommen-{i}"
						label={t.einkommen.frage}
						hilfe={t.einkommen.hilfe}
						einheit="Fr."
						min="0"
						bind:wert={person.einkommen}
						fehler={fehler[`eltern.${i}.einkommen`]}
					/>
				</div>
			</div>
		{/each}

		{#each kinder as kind, i (kind.nr)}
			<div class="unterblock">
				<div class="kopf">
					<h3>{einsetzen(t.kind, { nr: i + 1 })}</h3>
					{#if kinder.length > 1}
						<button
							type="button"
							class="link"
							onclick={() => {
								kinder = kinder.filter((k) => k.nr !== kind.nr);
								tageEigen = {};
								vergleichKind = 0;
							}}>{t.kind_entfernen}</button
						>
					{/if}
				</div>
				<Feld
					id="geburtsdatum-{kind.nr}"
					typ="date"
					label={t.geburtsdatum.frage}
					bind:wert={kind.geburtsdatum}
					fehler={fehler[`kind.${i}.geburtsdatum`]}
				/>
				<Auswahl
					name="eingeschult-{kind.nr}"
					frage={t.eingeschult.frage}
					optionen={JA_NEIN}
					bind:wert={kind.eingeschult}
					fehler={fehler[`kind.${i}.eingeschult`]}
				/>
				<Auswahl
					name="form-{kind.nr}"
					frage={t.form_heute.frage}
					optionen={formOptionen(kind)}
					bind:wert={kind.form}
					fehler={fehler[`kind.${i}.form`]}
				/>
				<div class="felder">
					{#each formenFuer({ eingeschult: kind.eingeschult === true }) as form (form)}
						<Feld
							id="preis-{kind.nr}-{form}"
							label={einsetzen(t.preis.frage, { form: KURZNAME[form] })}
							hilfe={t.preis.hilfe}
							einheit="Fr./Std."
							min="0"
							step="0.5"
							bind:wert={kind.preise[form]}
							fehler={fehler[`kind.${i}.preis.${form}`]}
						/>
						<Feld
							id="stunden-{kind.nr}-{form}"
							label={einsetzen(t.stunden.frage, { form: KURZNAME[form] })}
							hilfe={t.stunden.hilfe}
							einheit="Std."
							min="0"
							max="24"
							bind:wert={kind.stunden[form]}
							fehler={fehler[`kind.${i}.stunden.${form}`]}
						/>
					{/each}
				</div>
			</div>
		{/each}
		<button type="button" class="zweitrangig" onclick={() => kinder.push(neuesKind())}>
			{t.kind_hinzufuegen}
		</button>
	</section>

	<section>
		<h2>{t.abschnitt_vergleich}</h2>
		{#if paar}
			<Auswahl name="variiert" frage={t.variiert.frage} optionen={personenOptionen} bind:wert={variiertWahl} />
		{/if}
		<Feld
			id="lohn100"
			label={t.lohn100.frage}
			hilfe={t.lohn100.hilfe}
			einheit="Fr."
			min="0"
			bind:wert={lohn100}
			fehler={fehler.lohn100}
		/>
		{#if kinder.length > 1}
			<Auswahl name="vergleich-kind" frage={t.vergleich_kind.frage} optionen={kinderOptionen} bind:wert={vergleichKind} />
		{/if}
	</section>

	<section>
		<h2>{t.abschnitt_betreuung}</h2>
		<p class="hinweis">{t.betreuung_hinweis}</p>
		<div class="tabelle-rahmen">
			<table class="tage">
				<thead>
					<tr>
						<th scope="col">{t.betreuung_spalte_pensum} ({personName})</th>
						{#each kinder as kind, k (kind.nr)}
							<th scope="col">{einsetzen(t.betreuung_spalte_kind, { kind: einsetzen(t.kind, { nr: k + 1 }) })}</th>
						{/each}
					</tr>
				</thead>
				<tbody>
					{#each stufen as stufe (stufe)}
						<tr class={[stufe === heute && 'heute']}>
							<th scope="row" class="figur">{stufe} %{stufe === heute ? ` (${t.tabelle.heute})` : ''}</th>
							{#each kinder as kind, k (kind.nr)}
								<td>
									<input
										class={['figur', tageEigen[stufe]?.[k] !== undefined && 'eigen']}
										type="number"
										min="0"
										max="5"
										step="0.5"
										aria-label="{einsetzen(t.kind, { nr: k + 1 })}, {stufe} %"
										value={tageWert(stufe, k)}
										oninput={(e) => tageSetzen(stufe, k, e.currentTarget.value)}
									/>
								</td>
							{/each}
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
		<button type="button" class="zweitrangig" onclick={() => (tageEigen = {})}>{t.vorschlag_zuruecksetzen}</button>
	</section>

	{#if versucht && Object.keys(meldungen).length}
		<p class="fehlerbox" role="alert">{t.fehlt}</p>
	{/if}
	{#each serverFehler as eintrag (eintrag.pfad + eintrag.meldung)}
		<p class="fehlerbox" role="alert">{eintrag.meldung}</p>
	{/each}
	<button type="submit" class="hauptknopf" disabled={laeuft}>{laeuft ? t.rechnet : t.vergleichen}</button>
</form>

{#if ergebnis}
	<section class="ergebnisse" aria-live="polite">
		<h2>{t.abschnitt_ergebnis}</h2>
		{#if veraltet}<p class="hinweis veraltet">{t.veraltet}</p>{/if}

		<div class="steuerung">
			<Auswahl
				name="ansicht"
				frage={t.ansicht.frage}
				optionen={[
					{ wert: 'kurz', text: t.ansicht.kurz },
					{ wert: 'lang', text: t.ansicht.lang }
				]}
				bind:wert={ansicht}
			/>
			<div class="regler">
				<label for="ziel">{t.ziel.frage}: <strong class="figur">{ziel} %</strong></label>
				<input id="ziel" type="range" min="0" max="100" step="10" bind:value={ziel} />
			</div>
		</div>
		<p class="hinweis">{ansicht === 'kurz' ? t.ansicht.kurz_text : t.ansicht.lang_text}</p>

		<div class="kennzahlen">
			<div class="karte">
				<p class="label">{einsetzen(t.kennzahlen.heute, { pensum: ergebnis.heute })}</p>
				<p class="zeile"><span>{t.kennzahlen.beitrag}</span><span class="figur">Fr. {franken(ergebnis.ausgangslage.beitrag)}</span></p>
				<p class="zeile"><span>{t.kennzahlen.restkosten}</span><span class="figur">Fr. {franken(ergebnis.ausgangslage.restkosten)}</span></p>
			</div>
			<div class="karte">
				<p class="label">{einsetzen(t.kennzahlen.neu, { pensum: ziel })}</p>
				{#if zielFall}
					<p class="zeile"><span>{t.kennzahlen.beitrag}</span><span class="figur">Fr. {franken(zielFall.beitrag)}</span></p>
					<p class="zeile"><span>{t.kennzahlen.restkosten}</span><span class="figur">Fr. {franken(zielFall.restkosten)}</span></p>
					<p class="zeile"><span>{t.kennzahlen.guenstigste}</span><span>{KURZNAME[zielFall.form]}</span></p>
				{/if}
			</div>
			<div class={['karte', 'hervorgehoben', mehrverdienst - mehrkosten < 0 && 'negativ']}>
				<p class="label">{t.kennzahlen.bleibt} {t.kennzahlen.pro_monat}</p>
				<p class="zeile"><span>{t.kennzahlen.mehrverdienst}</span><span class="figur">Fr. {franken(mehrverdienst)}</span></p>
				<p class="zeile"><span>{t.kennzahlen.mehrkosten}</span><span class="figur">Fr. {franken(mehrkosten)}</span></p>
				<p class="gross figur">Fr. {franken(mehrverdienst - mehrkosten)}</p>
			</div>
		</div>

		<div class="karte chart">
			<LinienChart
				titel={t.chart_restkosten.titel}
				x={stufenErgebnis}
				{serien}
				{bereiche}
				markiertesX={ziel}
				xTitel={einsetzen(t.chart_restkosten.x, { person: personName })}
				yTitel={t.chart_restkosten.y}
				formatX={prozent}
				formatY={rund}
			/>
		</div>

		<div class="karte chart">
			<div class="kopf">
				<p class="text">{t.chart_bleibt.text}</p>
				<label class="auswahl-klein">
					{t.chart_bleibt.form}
					<select bind:value={balkenForm}>
						<option value="beste">{t.tabelle.guenstigste}</option>
						{#each formenErgebnis as form (form)}
							<option value={form}>{KURZNAME[form]}</option>
						{/each}
					</select>
				</label>
			</div>
			<BalkenChart
				titel={t.chart_bleibt.titel}
				x={stufenErgebnis}
				werte={balken}
				markiertesX={ziel}
				xTitel={einsetzen(t.chart_restkosten.x, { person: personName })}
				formatX={prozent}
				formatY={rund}
			/>
		</div>

		<div class="karte">
			<p class="tabellentitel">{t.tabelle.titel} ({ansicht === 'kurz' ? t.ansicht.kurz : t.ansicht.lang})</p>
			<div class="tabelle-rahmen">
				<table class="vergleich">
					<thead>
						<tr>
							<th scope="col">{t.tabelle.pensum}</th>
							{#each formenErgebnis as form (form)}<th scope="col">{KURZNAME[form]}</th>{/each}
						</tr>
					</thead>
					<tbody>
						{#each stufenErgebnis as stufe (stufe)}
							{@const bester = beste(stufe)}
							<tr class={[stufe === ergebnis.heute && 'heute', stufe === ziel && 'ziel']}>
								<th scope="row" class="figur">{stufe} %{stufe === ergebnis.heute ? ` (${t.tabelle.heute})` : ''}</th>
								{#each formenErgebnis as form (form)}
									{@const e = fall(form, stufe)}
									<td class={['figur', bester && e && bester.form === form && e.restkosten > 0 && 'beste']}>
										{e ? franken(e.restkosten) : '–'}
										{#if e && !e.anspruch && e.restkosten > 0}<span class="klein">{t.tabelle.kein_anspruch}</span>{/if}
									</td>
								{/each}
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		</div>

		<div class="karte">
			<p class="tabellentitel">{t.hinweise.titel}</p>
			<ul class="hinweise">
				<li>{t.hinweise.schwelle_20}</li>
				{#if paar}<li>{t.hinweise.schwelle_120}</li>{/if}
				<li>{t.hinweise.einkommen}</li>
				<li>{t.hinweise.ausnahme}</li>
				<li>{t.hinweise.zwoelf_stunden}</li>
			</ul>
			<p class="annahmen">{t.annahmen}</p>
		</div>
	</section>
{/if}

<style>
	h2 {
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

	form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	/* Abschnitte als Karten: Fläche und 1px-Linie statt Schatten (Style-Kit) */
	section,
	.karte {
		padding: 1.25rem;
		background: var(--card);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
	}

	section.ergebnisse {
		margin-top: 2.5rem;
		padding: 0;
		background: none;
		border: 0;
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.unterblock {
		margin-top: 1.25rem;
		padding-top: 1.25rem;
		border-top: 1px solid var(--border);
	}

	.unterblock h3 {
		margin: 0;
		font-size: var(--text-base);
		font-weight: 600;
	}

	.kopf {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 1rem;
	}

	.felder {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(15rem, 1fr));
		column-gap: 1.5rem;
	}

	.hinweis {
		margin: 0.5rem 0 0;
		color: var(--muted-foreground);
		font-size: var(--text-sm);
	}

	.veraltet {
		color: var(--destructive);
	}

	button {
		font: inherit;
		font-size: var(--text-sm);
		cursor: pointer;
		border-radius: var(--radius-md);
	}

	button:focus-visible,
	select:focus-visible,
	input:focus-visible {
		outline: 3px solid var(--ring);
		outline-offset: 1px;
	}

	.hauptknopf {
		align-self: flex-start;
		height: 2.5rem;
		padding: 0 1.5rem;
		background: var(--primary);
		color: var(--primary-foreground);
		border: 0;
		font-weight: 500;
	}

	.hauptknopf:hover {
		opacity: 0.85;
	}

	.hauptknopf:disabled {
		opacity: 0.5;
		cursor: wait;
	}

	.zweitrangig {
		margin-top: 1.25rem;
		height: 2.25rem;
		padding: 0 0.875rem;
		background: var(--card);
		color: var(--foreground);
		border: 1px solid var(--input);
	}

	.zweitrangig:hover {
		background: var(--secondary);
	}

	.link {
		background: none;
		border: 0;
		padding: 0;
		color: var(--primary);
		text-underline-offset: 4px;
	}

	.link:hover {
		text-decoration: underline;
	}

	.fehlerbox {
		margin: 0;
		padding: 0.625rem 0.75rem;
		border: 1px solid var(--destructive);
		border-radius: var(--radius-md);
		color: var(--destructive);
		font-size: var(--text-sm);
	}

	/* Tabellen */
	.tabelle-rahmen {
		overflow-x: auto;
		margin-top: 0.75rem;
	}

	table {
		border-collapse: collapse;
		width: 100%;
		font-size: var(--text-sm);
	}

	th,
	td {
		padding: 0.375rem 0.625rem;
		border-bottom: 1px solid var(--border);
		text-align: right;
		white-space: nowrap;
	}

	th:first-child {
		text-align: left;
	}

	thead th {
		font-weight: 500;
		color: var(--muted-foreground);
	}

	tr.heute th {
		color: var(--primary);
	}

	tr.ziel {
		background: var(--secondary);
	}

	.tage input {
		width: 5rem;
		height: 2rem;
		padding: 0 0.5rem;
		border: 1px solid var(--input);
		border-radius: var(--radius-md);
		background: var(--card);
		text-align: right;
		font: inherit;
	}

	.tage input.eigen {
		border-color: var(--primary);
		background: color-mix(in oklch, var(--primary) 6%, var(--card));
	}

	td.beste {
		color: var(--primary);
		font-weight: 600;
	}

	.klein {
		display: block;
		font-family: var(--font-sans);
		font-size: var(--text-xs);
		color: var(--destructive);
	}

	/* Steuerung des Ergebnisses */
	.steuerung {
		display: flex;
		flex-wrap: wrap;
		align-items: flex-end;
		gap: 0.5rem 2rem;
	}

	.regler {
		margin: 1.25rem 0;
		min-width: 16rem;
	}

	.regler label {
		display: block;
		font-size: var(--text-sm);
		font-weight: 500;
		margin-bottom: 0.375rem;
	}

	.regler input {
		width: 100%;
		accent-color: var(--primary);
	}

	/* Kennzahlen */
	.kennzahlen {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(15rem, 1fr));
		gap: 1rem;
	}

	.kennzahlen .label {
		margin: 0 0 0.5rem;
	}

	.zeile {
		display: flex;
		justify-content: space-between;
		gap: 1rem;
		margin: 0.25rem 0;
		font-size: var(--text-sm);
	}

	.zeile .figur,
	.gross {
		white-space: nowrap;
	}

	.hervorgehoben {
		border-left: 4px solid var(--gruen-wappen);
	}

	.hervorgehoben.negativ {
		border-left-color: var(--destructive);
	}

	.gross {
		margin: 0.5rem 0 0;
		font-size: var(--text-xl);
		font-weight: 600;
		color: var(--primary);
	}

	.negativ .gross {
		color: var(--destructive);
	}

	.chart .kopf {
		flex-wrap: wrap;
	}

	.chart .text {
		flex: 1 1 18rem;
		margin: 0 0 0.75rem;
		color: var(--muted-foreground);
		font-size: var(--text-sm);
	}

	.auswahl-klein {
		display: inline-flex;
		align-items: center;
		gap: 0.5rem;
		font-size: var(--text-sm);
		white-space: nowrap;
	}

	select {
		font: inherit;
		font-size: var(--text-sm);
		height: 2rem;
		padding: 0 0.5rem;
		border: 1px solid var(--input);
		border-radius: var(--radius-md);
		background: var(--card);
	}

	.tabellentitel {
		margin: 0;
		font-size: var(--text-sm);
		font-weight: 600;
	}

	.hinweise {
		margin: 0.5rem 0 0;
		padding-left: 1.25rem;
		font-size: var(--text-sm);
	}

	.hinweise li {
		margin: 0.25rem 0;
	}

	.annahmen {
		margin: 0.75rem 0 0;
		color: var(--muted-foreground);
		font-size: var(--text-xs);
	}
</style>
