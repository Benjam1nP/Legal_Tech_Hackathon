<script>
	import Auswahl from '#lib/Auswahl.svelte';
	import Feld from '#lib/Feld.svelte';
	import Ergebnis from '#lib/Ergebnis.svelte';
	import { texte, einsetzen } from '#lib/darstellung.js';

	const f = texte.formular;
	const fb = texte.fragebogen;
	const JA_NEIN = [
		{ wert: true, text: f.ja },
		{ wert: false, text: f.nein }
	];
	const EINRICHTUNGEN = Object.entries(fb.kind.kibg_einrichtungstyp.optionen).map(
		([wert, text]) => ({ wert, text })
	);

	const neuerElternteil = () => ({ wohnsitz: null, pensum: null, einkommen: null, aktuell: null });
	let naechsteKindNr = 1;
	const neuesKind = () => ({
		nr: naechsteKindNr++,
		geburtsdatum: '',
		betreuungsbeginn: '',
		gesuchsdatum: '',
		eingeschult: null,
		primarschuleAbgeschlossen: null,
		typ: null,
		anerkannt: null,
		angemeldet: null,
		bestaetigtAm: '',
		jahrKindergarten: null,
		tage: null,
		stunden: null,
		kosten: null
	});

	// Angaben im Formular
	let monat = $state('2028-09');
	let gemeinsam = $state(null);
	let eltern = $state([neuerElternteil(), neuerElternteil()]);
	let partner = $state({ vorhanden: null, verheiratet: null, seit: '', einkommen: null, aktuell: null });
	let antragAktuell = $state(false);
	let ausnahme = $state(false);
	let kinder = $state([neuesKind()]);

	// Zustand der Berechnung. Nach dem ersten Klick auf «Berechnen» werden die
	// Pflichtangaben laufend geprüft: Eine Meldung verschwindet, sobald das Feld
	// ausgefüllt ist. Fehler von OpenFisca gelten, bis die Angaben ändern.
	let versucht = $state(false);
	let serverFehler = $state({});
	let serverFehlerFuer = $state('');
	let ergebnis = $state.raw(null);
	let berechnetMit = $state('');
	// Angaben, mit denen das Ergebnis berechnet wurde. Das Ergebnis zeigt diese,
	// nicht das Formular: Sonst mischen sich nach einer Änderung alte und neue
	// Werte, und ein entferntes Kind fehlt in den Angaben.
	let berechnet = $derived(berechnetMit ? JSON.parse(berechnetMit) : null);
	let laeuft = $state(false);

	// Bei gemeinsamem Haushalt zwei Erziehungsberechtigte, sonst nur die
	// gesuchstellende Person (Art. 2 Abs. 1 KiBG, Entscheid zu getrennten Eltern).
	let anzahlEltern = $derived(gemeinsam === true ? 2 : 1);
	let mitPartner = $derived(gemeinsam === false && partner.vorhanden === true);

	// Wer das Gesuch stellt, wird nicht gefragt (Teamentscheid): Es genügt, dass
	// eine der beiden Personen im Kanton St. Gallen wohnt. Gesuchstellend ist
	// deshalb die erste Person mit Wohnsitz im Kanton, sonst Person 1.
	let gesuchstellerIndex = $derived(
		Math.max(0, eltern.slice(0, anzahlEltern).findIndex((p) => p.wohnsitz === true))
	);

	let angaben = $derived({
		monat,
		gemeinsam,
		gesuchsteller: anzahlEltern === 2 ? gesuchstellerIndex : 0,
		eltern: eltern.slice(0, anzahlEltern),
		partner: { ...partner, vorhanden: mitPartner },
		antragAktuell,
		ausnahme,
		kinder
	});
	let veraltet = $derived(ergebnis !== null && JSON.stringify(angaben) !== berechnetMit);
	let fehler = $derived.by(() => {
		if (!versucht) return {};
		const aktuell = JSON.stringify(angaben) === serverFehlerFuer ? serverFehler : {};
		return { ...pruefen(), ...aktuell };
	});

	const leer = (wert) => wert === null || wert === '' || Number.isNaN(wert);
	// «Kind 1» wie «Person 1»: passt grammatisch in jeden Satz der Texte.
	const kindName = (index) => `Kind ${index + 1}`;
	const monatsname = (datum) =>
		new Date(`${datum.slice(0, 7)}-01T00:00:00`).toLocaleDateString('de-CH', {
			month: 'long',
			year: 'numeric'
		});
	const personName = (index) =>
		anzahlEltern === 1 ? f.person_einzeln : einsetzen(f.person, { nr: index + 1 });

	/** Pflichtangaben prüfen. Ergebnis: { feld: meldung }. */
	function pruefen() {
		const meldungen = {};
		const pflicht = (feld, wert) => {
			if (leer(wert)) meldungen[feld] = f.pflicht;
		};
		const betrag = (feld, wert) => {
			if (leer(wert)) meldungen[feld] = f.pflicht;
			else if (Number(wert) < 0) meldungen[feld] = f.ungueltig;
		};

		if (leer(monat)) meldungen.monat = f.pflicht;
		else if (monat < '2028-08') meldungen.monat = f.monat_zu_frueh;
		pflicht('gemeinsam', gemeinsam);
		if (gemeinsam === false) {
			pflicht('partner.vorhanden', partner.vorhanden);
			if (partner.vorhanden === true) {
				pflicht('partner.verheiratet', partner.verheiratet);
				if (partner.verheiratet === false) pflicht('partner.seit', partner.seit);
				betrag('partner.einkommen', partner.einkommen);
				if (antragAktuell) betrag('partner.aktuell', partner.aktuell);
			}
		}
		eltern.slice(0, anzahlEltern).forEach((person, i) => {
			pflicht(`elternteil_${i + 1}.wohnsitz`, person.wohnsitz);
			betrag(`elternteil_${i + 1}.pensum`, person.pensum);
			betrag(`elternteil_${i + 1}.einkommen`, person.einkommen);
			if (antragAktuell) betrag(`elternteil_${i + 1}.aktuell`, person.aktuell);
		});
		kinder.forEach((kind, i) => {
			const id = `kind_${i + 1}`;
			pflicht(`${id}.geburtsdatum`, kind.geburtsdatum);
			pflicht(`${id}.betreuungsbeginn`, kind.betreuungsbeginn);
			pflicht(`${id}.gesuchsdatum`, kind.gesuchsdatum);
			pflicht(`${id}.eingeschult`, kind.eingeschult);
			if (kind.eingeschult === true) {
				pflicht(`${id}.primarschuleAbgeschlossen`, kind.primarschuleAbgeschlossen);
			}
			pflicht(`${id}.typ`, kind.typ);
			if (kind.typ && kind.typ !== 'keine') {
				pflicht(`${id}.anerkannt`, kind.anerkannt);
				pflicht(`${id}.angemeldet`, kind.angemeldet);
			}
			betrag(`${id}.tage`, kind.tage);
			betrag(`${id}.stunden`, kind.stunden);
			betrag(`${id}.kosten`, kind.kosten);
		});
		return meldungen;
	}

	// Fehler von OpenFisca (Pfad wie persons/kind_1/geburtsdatum) dem
	// Formularfeld zuordnen und die verständliche Meldung aus texte.de.json nehmen.
	const OPENFISCA_FELDER = {
		gemeinsamer_haushalt: 'gemeinsam',
		betreuungstage_mit_obhut: 'tage',
		kibg_gesuchsdatum: 'gesuchsdatum',
		kibg_einrichtung_angemeldet: 'angemeldet',
		kibg_einrichtung_bestaetigt_am: 'bestaetigtAm',
		me_aktuell: 'aktuell',
		me_steuerveranlagung: 'einkommen'
	};
	function fehlerZuordnen(liste) {
		const meldungen = {};
		for (const { pfad, meldung } of liste) {
			const [, id, variable] = pfad.split('/');
			const feld = OPENFISCA_FELDER[variable] ?? variable ?? '';
			const schluessel = feld === 'gemeinsam' ? feld : `${id}.${feld}`;
			const kindIndex = id?.startsWith('kind_') ? Number(id.slice(5)) - 1 : 0;
			// Zwei Prüfungen melden sich beim Feld der Betreuungstage: Tage fehlen
			// (Art. 14 Abs. 4 KiBV) oder mehr Tage als ab dem Beitragsbeginn (A9).
			// Dazu kommt: mehr Tage als bis zum Ende der Verfügung (A12).
			const text =
				variable === 'betreuungstage_mit_obhut' && meldung.includes('Beitragsbeginn')
					? texte.fehler.betreuungstage_ab_beitragsbeginn
					: variable === 'betreuungstage_mit_obhut' && meldung.includes('Verfügung')
						? texte.fehler.betreuungstage_bis_verfuegungsende
						: texte.fehler[variable];
			meldungen[pfad ? schluessel : 'allgemein'] = text
				? einsetzen(text, { kind: kindName(kindIndex) })
				: meldung;
		}
		return meldungen;
	}

	async function berechnen() {
		versucht = true;
		serverFehler = {};
		if (Object.keys(pruefen()).length) {
			ergebnis = null;
			return;
		}
		laeuft = true;
		const gesendet = JSON.stringify(angaben);
		try {
			const antwort = await fetch('/api/berechnen', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: gesendet
			});
			const inhalt = await antwort.json();
			if (inhalt.fehler) {
				serverFehler = fehlerZuordnen(inhalt.fehler);
				serverFehlerFuer = gesendet;
				ergebnis = null;
			} else {
				ergebnis = inhalt;
				berechnetMit = gesendet;
			}
		} catch {
			serverFehler = { allgemein: texte.fehler.allgemein };
			serverFehlerFuer = gesendet;
			ergebnis = null;
		} finally {
			laeuft = false;
		}
	}

	// Frage zu einem Feld, für die Liste der fehlenden Angaben.
	const FRAGEN = {
		wohnsitz: fb.personen.wohnsitz_kanton_sg,
		pensum: fb.personen.beschaeftigungsgrad,
		einkommen: fb.personen.me_steuerveranlagung,
		aktuell: fb.personen.me_aktuell,
		geburtsdatum: fb.kind.geburtsdatum,
		betreuungsbeginn: fb.kind.betreuungsbeginn,
		gesuchsdatum: fb.kind.kibg_gesuchsdatum,
		eingeschult: fb.kind.eingeschult,
		primarschuleAbgeschlossen: fb.kind.primarschule_abgeschlossen,
		typ: fb.kind.kibg_einrichtungstyp,
		anerkannt: fb.kind.kibg_einrichtung_anerkannt,
		angemeldet: fb.kind.kibg_einrichtung_angemeldet,
		bestaetigtAm: fb.kind.kibg_einrichtung_bestaetigt_am,
		tage: fb.kind.betreuungstage_mit_obhut,
		stunden: fb.kind.betreuungsstunden,
		kosten: fb.kind.kibg_betreuungskosten
	};
	const PARTNER_FRAGEN = {
		vorhanden: fb.haushalt.partner_vorhanden,
		verheiratet: fb.haushalt.verheiratet_oder_eingetragen,
		seit: fb.haushalt.beginn_gemeinsamer_haushalt,
		einkommen: fb.haushalt.partner_einkommen,
		aktuell: fb.haushalt.partner_aktuell
	};
	function feldname(schluessel) {
		if (schluessel === 'monat') return f.monat.frage;
		if (schluessel === 'gemeinsam') return fb.haushalt.gemeinsamer_haushalt.frage;
		const [wer, feld] = schluessel.split('.');
		if (wer === 'partner') return `${f.partner_titel}: ${PARTNER_FRAGEN[feld]?.frage}`;
		const nr = Number(wer.split('_')[1]) - 1;
		const name = wer.startsWith('kind') ? kindName(nr) : personName(nr);
		return `${name}: ${FRAGEN[feld]?.frage ?? feld}`;
	}
	let fehlend = $derived(
		Object.keys(fehler)
			.filter((k) => k !== 'allgemein')
			.map(feldname)
	);

	let summe = $derived.by(() => {
		if (!ergebnis || !berechnet) return null;
		const add = (name) => ergebnis.kinder.reduce((s, k) => s + Number(k[name]), 0);
		return {
			summe_beitrag_total: add('kibg_beitrag_total'),
			summe_restkosten: add('kibg_restkosten_eltern'),
			summe_kosten: berechnet.kinder.reduce((s, k) => s + Number(k.kosten), 0)
		};
	});
</script>

<p class="einleitung">{f.einleitung}</p>

<form
	novalidate
	onsubmit={(event) => {
		event.preventDefault();
		berechnen();
	}}
>
	<section>
		<h2>{f.abschnitt_haushalt}</h2>
		<Feld
			id="monat"
			typ="month"
			min="2028-08"
			label={f.monat.frage}
			hilfe={f.monat.hilfe}
			bind:wert={monat}
			fehler={fehler.monat}
		/>
		<Auswahl
			name="gemeinsam"
			frage={fb.haushalt.gemeinsamer_haushalt.frage}
			hilfe={fb.haushalt.gemeinsamer_haushalt.hilfe}
			optionen={JA_NEIN}
			bind:wert={gemeinsam}
			fehler={fehler.gemeinsam}
		/>
		{#if gemeinsam === false}
			<Auswahl
				name="partner"
				frage={fb.haushalt.partner_vorhanden.frage}
				hilfe={fb.haushalt.partner_vorhanden.hilfe}
				optionen={JA_NEIN}
				bind:wert={partner.vorhanden}
				fehler={fehler['partner.vorhanden']}
			/>
			{#if partner.vorhanden === true}
				<div class="unterblock">
					<h3>{f.partner_titel}</h3>
					<Auswahl
						name="verheiratet"
						frage={fb.haushalt.verheiratet_oder_eingetragen.frage}
						optionen={JA_NEIN}
						bind:wert={partner.verheiratet}
						fehler={fehler['partner.verheiratet']}
					/>
					{#if partner.verheiratet === false}
						<Feld
							id="partner-seit"
							typ="date"
							label={fb.haushalt.beginn_gemeinsamer_haushalt.frage}
							bind:wert={partner.seit}
							fehler={fehler['partner.seit']}
						/>
					{/if}
					<Feld
						id="partner-einkommen"
						label={fb.haushalt.partner_einkommen.frage}
						hilfe={fb.haushalt.partner_einkommen.hilfe}
						einheit="Fr."
						min="0"
						bind:wert={partner.einkommen}
						fehler={fehler['partner.einkommen']}
					/>
					{#if antragAktuell}
						<Feld
							id="partner-aktuell"
							label={fb.haushalt.partner_aktuell.frage}
							einheit="Fr."
							min="0"
							bind:wert={partner.aktuell}
							fehler={fehler['partner.aktuell']}
						/>
					{/if}
				</div>
			{/if}
		{/if}
	</section>

	<section>
		<h2>{f.abschnitt_personen}</h2>
		{#each { length: anzahlEltern }, i}
			<div class="unterblock">
				<h3>{personName(i)}</h3>
				<Auswahl
					name="wohnsitz-{i}"
					frage={fb.personen.wohnsitz_kanton_sg.frage}
					optionen={JA_NEIN}
					bind:wert={eltern[i].wohnsitz}
					fehler={fehler[`elternteil_${i + 1}.wohnsitz`]}
				/>
				<Feld
					id="pensum-{i}"
					label={fb.personen.beschaeftigungsgrad.frage}
					hilfe={fb.personen.beschaeftigungsgrad.hilfe}
					einheit="%"
					min="0"
					bind:wert={eltern[i].pensum}
					fehler={fehler[`elternteil_${i + 1}.pensum`]}
				/>
				<Feld
					id="einkommen-{i}"
					label={fb.personen.me_steuerveranlagung.frage}
					hilfe={fb.personen.me_steuerveranlagung.hilfe}
					einheit="Fr."
					min="0"
					bind:wert={eltern[i].einkommen}
					fehler={fehler[`elternteil_${i + 1}.einkommen`]}
				/>
				{#if antragAktuell}
					<Feld
						id="aktuell-{i}"
						label={fb.personen.me_aktuell.frage}
						einheit="Fr."
						min="0"
						bind:wert={eltern[i].aktuell}
						fehler={fehler[`elternteil_${i + 1}.aktuell`]}
					/>
				{/if}
			</div>
		{/each}
		<Auswahl
			name="antrag"
			frage={fb.personen.kibg_antrag_aktuelle_gegebenheiten.frage}
			hilfe={fb.personen.kibg_antrag_aktuelle_gegebenheiten.hilfe}
			optionen={JA_NEIN}
			bind:wert={antragAktuell}
		/>
		<Auswahl
			name="ausnahme"
			frage={fb.personen.kibg_ausnahme_bewilligt.frage}
			hilfe={fb.personen.kibg_ausnahme_bewilligt.hilfe}
			optionen={JA_NEIN}
			bind:wert={ausnahme}
		/>
	</section>

	<section>
		<h2>{f.abschnitt_kinder}</h2>
		{#each kinder as kind, i (kind.nr)}
			<div class="unterblock">
				<div class="kopf">
					<h3>{einsetzen(fb.kind.titel, { kind: kindName(i) })}</h3>
					{#if kinder.length > 1}
						<button
							type="button"
							class="link"
							onclick={() => (kinder = kinder.filter((k) => k.nr !== kind.nr))}
						>
							{f.kind_entfernen}
						</button>
					{/if}
				</div>
				<Feld
					id="geburtsdatum-{kind.nr}"
					typ="date"
					label={fb.kind.geburtsdatum.frage}
					bind:wert={kind.geburtsdatum}
					fehler={fehler[`kind_${i + 1}.geburtsdatum`]}
				/>
				<Feld
					id="betreuungsbeginn-{kind.nr}"
					typ="date"
					label={fb.kind.betreuungsbeginn.frage}
					hilfe={fb.kind.betreuungsbeginn.hilfe}
					bind:wert={kind.betreuungsbeginn}
					fehler={fehler[`kind_${i + 1}.betreuungsbeginn`]}
				/>
				{#if kind.betreuungsbeginn && monat && monat < kind.betreuungsbeginn.slice(0, 7)}
					<!-- Nur ein Hinweis zur Eingabe; ab wann Beiträge fliessen, rechnet
					     OpenFisca (Art. 9 Abs. 2 KiBG, Art. 25 KiBV). -->
					<p class="hinweis-monat">
						{einsetzen(f.monat_vor_betreuungsbeginn, { kind: kindName(i) })}
						<button
							type="button"
							class="link"
							onclick={() => (monat = kind.betreuungsbeginn.slice(0, 7))}
						>
							{einsetzen(f.monat_uebernehmen, { monat: monatsname(kind.betreuungsbeginn) })}
						</button>
					</p>
				{/if}
				<Feld
					id="gesuchsdatum-{kind.nr}"
					typ="date"
					label={fb.kind.kibg_gesuchsdatum.frage}
					hilfe={fb.kind.kibg_gesuchsdatum.hilfe}
					bind:wert={kind.gesuchsdatum}
					fehler={fehler[`kind_${i + 1}.gesuchsdatum`]}
				/>
				<Auswahl
					name="eingeschult-{kind.nr}"
					frage={fb.kind.eingeschult.frage}
					optionen={JA_NEIN}
					bind:wert={kind.eingeschult}
					fehler={fehler[`kind_${i + 1}.eingeschult`]}
				/>
				{#if kind.eingeschult === true}
					<Auswahl
						name="primarschule-{kind.nr}"
						frage={fb.kind.primarschule_abgeschlossen.frage}
						optionen={JA_NEIN}
						bind:wert={kind.primarschuleAbgeschlossen}
						fehler={fehler[`kind_${i + 1}.primarschuleAbgeschlossen`]}
					/>
				{/if}
				{#if kind.eingeschult === false}
					<Feld
						id="kindergarten-{kind.nr}"
						label={fb.kind.jahr_eintritt_kindergarten.frage}
						hilfe={fb.kind.jahr_eintritt_kindergarten.hilfe}
						min="2028"
						step="1"
						bind:wert={kind.jahrKindergarten}
					/>
				{/if}
				<Auswahl
					name="typ-{kind.nr}"
					frage={fb.kind.kibg_einrichtungstyp.frage}
					optionen={EINRICHTUNGEN}
					bind:wert={kind.typ}
					fehler={fehler[`kind_${i + 1}.typ`]}
				/>
				{#if kind.typ && kind.typ !== 'keine'}
					<Auswahl
						name="anerkannt-{kind.nr}"
						frage={fb.kind.kibg_einrichtung_anerkannt.frage}
						hilfe={fb.kind.kibg_einrichtung_anerkannt.hilfe}
						optionen={JA_NEIN}
						bind:wert={kind.anerkannt}
						fehler={fehler[`kind_${i + 1}.anerkannt`]}
					/>
					<Auswahl
						name="angemeldet-{kind.nr}"
						frage={fb.kind.kibg_einrichtung_angemeldet.frage}
						hilfe={fb.kind.kibg_einrichtung_angemeldet.hilfe}
						optionen={JA_NEIN}
						bind:wert={kind.angemeldet}
						fehler={fehler[`kind_${i + 1}.angemeldet`]}
					/>
					<!-- Das Datum der Bestätigung kennen Eltern selten: eingeklappt,
					     offen nur wenn ausgefüllt -->
					<details class="weitere" open={!!kind.bestaetigtAm}>
						<summary>{fb.kind.weitere_angaben}</summary>
						<Feld
							id="bestaetigt-{kind.nr}"
							typ="date"
							label={fb.kind.kibg_einrichtung_bestaetigt_am.frage}
							hilfe={fb.kind.kibg_einrichtung_bestaetigt_am.hilfe}
							bind:wert={kind.bestaetigtAm}
							fehler={fehler[`kind_${i + 1}.bestaetigtAm`]}
						/>
					</details>
				{/if}
				<Feld
					id="tage-{kind.nr}"
					label={fb.kind.betreuungstage_mit_obhut.frage}
					hilfe={fb.kind.betreuungstage_mit_obhut.hilfe}
					einheit="Tage"
					min="0"
					step="1"
					bind:wert={kind.tage}
					fehler={fehler[`kind_${i + 1}.tage`]}
				/>
				<Feld
					id="stunden-{kind.nr}"
					label={fb.kind.betreuungsstunden.frage}
					einheit="Stunden"
					min="0"
					bind:wert={kind.stunden}
					fehler={fehler[`kind_${i + 1}.stunden`]}
				/>
				<Feld
					id="kosten-{kind.nr}"
					label={fb.kind.kibg_betreuungskosten.frage}
					hilfe={fb.kind.kibg_betreuungskosten.hilfe}
					einheit="Fr."
					min="0"
					bind:wert={kind.kosten}
					fehler={fehler[`kind_${i + 1}.kosten`]}
				/>
			</div>
		{/each}
		<button type="button" class="zweitrangig" onclick={() => kinder.push(neuesKind())}>
			{f.kind_hinzufuegen}
		</button>
	</section>

	{#if Object.keys(fehler).length}
		<div class="fehlerliste" role="alert">
			{#if fehler.allgemein}
				<p>{fehler.allgemein}</p>
			{/if}
			{#if fehlend.length}
				<p>{f.fehlt_titel}</p>
				<ul>
					{#each fehlend as name (name)}
						<li>{name}</li>
					{/each}
				</ul>
			{/if}
		</div>
	{/if}

	<button type="submit" class="hauptknopf" disabled={laeuft}>
		{laeuft ? f.rechnet : f.berechnen}
	</button>
</form>

{#if ergebnis && berechnet}
	<section class="ergebnisse" aria-live="polite">
		<h2>{f.ergebnis_titel}</h2>
		{#if veraltet}
			<p class="veraltet">{f.veraltet}</p>
		{/if}
		{#each ergebnis.kinder as kind, i (i)}
			<Ergebnis
				bezeichnung={kindName(i)}
				{kind}
				eingabe={berechnet.kinder[i]}
				haushalt={ergebnis.haushalt}
				angaben={berechnet}
				partnerEinkommenZaehlt={ergebnis.partnerEinkommenZaehlt}
			/>
		{/each}
		{#if ergebnis.kinder.length > 1 && summe}
			<div class="familie">
				<h3>{texte.ergebnis.familie.titel}</h3>
				<p>{einsetzen(texte.ergebnis.familie.text, summe)}</p>
			</div>
		{/if}
	</section>
{/if}

<p class="fester-hinweis">{texte.fester_hinweis}</p>

<style>
	.einleitung {
		margin: 0 0 1.5rem;
		color: var(--muted-foreground);
	}

	form {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	/* Abschnitte als Karten: Fläche und 1px-Linie statt Schatten (Style-Kit) */
	section {
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
	}

	/* Abschnittstitel im Grün des Kantons St. Gallen */
	h2 {
		margin: 0;
		font-size: var(--text-xl);
		line-height: 1.75rem;
		font-weight: 700;
		color: var(--gruen-wappen);
	}

	/* Unterblöcke (Person 1, Kind 1 …) durch eine Linie getrennt */
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

	button {
		font: inherit;
		font-size: var(--text-sm);
		cursor: pointer;
		border-radius: var(--radius-md);
		transition:
			background-color 100ms ease-out,
			opacity 100ms ease-out;
	}

	button:active {
		transform: translateY(1px);
	}

	button:focus-visible {
		outline: 3px solid var(--ring);
		outline-offset: 1px;
	}

	/* Der einzige grüne Hauptknopf der Seite */
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

	/* Freiwillige Angaben, eingeklappt */
	.weitere {
		margin-bottom: 1rem;
	}

	.weitere summary {
		cursor: pointer;
		font-size: var(--text-sm);
		color: var(--primary);
		margin-bottom: 0.75rem;
	}

	.weitere summary:focus-visible {
		outline: 3px solid var(--ring);
		border-radius: var(--radius-md);
	}

	.hinweis-monat {
		margin: -0.5rem 0 1rem;
		padding: 0.625rem 0.75rem;
		background: var(--secondary);
		border-radius: var(--radius-md);
		font-size: var(--text-sm);
	}

	/* Fehlende Angaben: ruhige Karte, Fehlerfarbe nur im Text */
	.fehlerliste {
		padding: 1rem 1.25rem;
		background: var(--card);
		border: 1px solid var(--border);
		border-left: 2px solid var(--destructive);
		border-radius: var(--radius-lg);
		font-size: var(--text-sm);
	}

	.fehlerliste p {
		margin: 0;
		font-weight: 500;
		color: var(--destructive);
	}

	.fehlerliste ul {
		margin: 0.5rem 0 0;
		padding-left: 1.25rem;
	}

	.veraltet {
		color: var(--muted-foreground);
		font-size: var(--text-sm);
	}

	.familie {
		padding: 1.25rem;
		background: var(--card);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
	}

	.familie h3 {
		margin: 0 0 0.25rem;
		font-size: var(--text-base);
		font-weight: 600;
	}

	.familie p {
		margin: 0;
	}

	.fester-hinweis {
		margin-top: 2.5rem;
		padding-top: 1.25rem;
		border-top: 1px solid var(--border);
		color: var(--muted-foreground);
		font-size: var(--text-sm);
	}
</style>
