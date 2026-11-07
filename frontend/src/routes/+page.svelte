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
		eingeschult: null,
		primarschuleAbgeschlossen: null,
		typ: null,
		anerkannt: null,
		angemeldet: null,
		tage: null,
		stunden: null,
		kosten: null
	});

	// Angaben im Formular
	let monat = $state('2028-09');
	let gemeinsam = $state(null);
	let gesuchsteller = $state(null);
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
	let laeuft = $state(false);

	// Bei gemeinsamem Haushalt zwei Erziehungsberechtigte, sonst nur die
	// gesuchstellende Person (Art. 2 Abs. 1 KiBG, Entscheid zu getrennten Eltern).
	let anzahlEltern = $derived(gemeinsam === true ? 2 : 1);
	let mitPartner = $derived(gemeinsam === false && partner.vorhanden === true);

	let angaben = $derived({
		monat,
		gemeinsam,
		gesuchsteller: anzahlEltern === 2 ? gesuchsteller : 0,
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
	const kindName = (index) => `${index + 1}. Kind`;
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
		if (gemeinsam === true) pflicht('gesuchsteller', gesuchsteller);
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
		kibg_gesuchstellend: 'gesuchsteller',
		betreuungstage_mit_obhut: 'tage',
		me_aktuell: 'aktuell',
		me_steuerveranlagung: 'einkommen'
	};
	function fehlerZuordnen(liste) {
		const meldungen = {};
		for (const { pfad, meldung } of liste) {
			const [, id, variable] = pfad.split('/');
			const feld = OPENFISCA_FELDER[variable] ?? variable ?? '';
			const schluessel = ['gemeinsam', 'gesuchsteller'].includes(feld) ? feld : `${id}.${feld}`;
			const kindIndex = id?.startsWith('kind_') ? Number(id.slice(5)) - 1 : 0;
			const text = texte.fehler[variable];
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
		eingeschult: fb.kind.eingeschult,
		primarschuleAbgeschlossen: fb.kind.primarschule_abgeschlossen,
		typ: fb.kind.kibg_einrichtungstyp,
		anerkannt: fb.kind.kibg_einrichtung_anerkannt,
		angemeldet: fb.kind.kibg_einrichtung_angemeldet,
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
		if (schluessel === 'gesuchsteller') return fb.haushalt.kibg_gesuchstellend.frage;
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
		if (!ergebnis) return null;
		const add = (name) => ergebnis.kinder.reduce((s, k) => s + Number(k[name]), 0);
		return {
			summe_beitrag_total: add('kibg_beitrag_total'),
			summe_restkosten: add('kibg_restkosten_eltern'),
			summe_kosten: kinder.reduce((s, k) => s + Number(k.kosten), 0)
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
		{#if gemeinsam === true}
			<Auswahl
				name="gesuchsteller"
				frage={fb.haushalt.kibg_gesuchstellend.frage}
				hilfe={fb.haushalt.kibg_gesuchstellend.hilfe}
				optionen={[
					{ wert: 0, text: einsetzen(f.person, { nr: 1 }) },
					{ wert: 1, text: einsetzen(f.person, { nr: 2 }) }
				]}
				bind:wert={gesuchsteller}
				fehler={fehler.gesuchsteller}
			/>
		{/if}
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

{#if ergebnis}
	<section class="ergebnisse" aria-live="polite">
		<h2>{f.ergebnis_titel}</h2>
		{#if veraltet}
			<p class="veraltet">{f.veraltet}</p>
		{/if}
		{#each ergebnis.kinder as kind, i (i)}
			<Ergebnis
				bezeichnung={kindName(i)}
				{kind}
				eingabe={kinder[i]}
				haushalt={ergebnis.haushalt}
				{angaben}
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
		margin-top: 0;
	}

	section {
		margin: 2rem 0;
	}

	h2 {
		font-size: 1.3rem;
		margin: 0 0 0.5rem;
		padding-bottom: 0.4rem;
		border-bottom: 2px solid var(--schwarz);
	}

	.unterblock {
		border-left: 3px solid var(--grau-linie);
		padding-left: 1rem;
		margin: 1.25rem 0;
	}

	.unterblock h3 {
		font-size: 1.1rem;
		margin: 0;
	}

	.kopf {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		gap: 1rem;
	}

	button {
		font: inherit;
		cursor: pointer;
		border-radius: 0;
	}

	button:focus-visible {
		outline: 3px solid var(--schwarz);
		outline-offset: 2px;
	}

	.hauptknopf {
		background: var(--gruen);
		color: var(--weiss);
		border: 2px solid var(--gruen);
		font-weight: 700;
		font-size: 1.15rem;
		padding: 0.75rem 2.5rem;
	}

	.hauptknopf:hover {
		background: var(--gruen-text);
		border-color: var(--gruen-text);
	}

	.hauptknopf:disabled {
		opacity: 0.6;
		cursor: wait;
	}

	.zweitrangig {
		background: var(--weiss);
		color: var(--schwarz);
		border: 1px solid var(--schwarz);
		padding: 0.5rem 1rem;
	}

	.zweitrangig:hover {
		background: var(--gruen-hell);
	}

	.link {
		background: none;
		border: 0;
		color: var(--schwarz);
		text-decoration: underline;
		padding: 0;
	}

	.fehlerliste {
		border-left: 6px solid var(--fehler);
		background: var(--grau-hell);
		padding: 0.75rem 1rem;
		margin-bottom: 1rem;
	}

	.fehlerliste p {
		margin: 0;
		font-weight: 600;
	}

	.fehlerliste ul {
		margin: 0.4rem 0 0;
		padding-left: 1.2rem;
	}

	.veraltet {
		font-weight: 600;
	}

	.familie {
		border-top: 2px solid var(--schwarz);
		padding-top: 0.75rem;
	}

	.familie h3 {
		margin: 0 0 0.25rem;
	}

	.fester-hinweis {
		margin-top: 2.5rem;
		padding-top: 1rem;
		border-top: 1px solid var(--grau-linie);
		color: var(--grau);
		font-size: 0.95rem;
	}
</style>
