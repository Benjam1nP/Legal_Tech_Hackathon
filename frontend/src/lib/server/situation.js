// Baut aus den Formularangaben die Situation für die OpenFisca-Web-API
// (/calculate) und liest die Ergebnisse wieder aus. Die Namen der Variablen
// stehen in challenge/line-to-line-rules.md.

// Werte, die OpenFisca für jedes Kind berechnen soll.
const ERGEBNISSE_KIND = [
	'kibg_anspruch',
	'kibg_alter_erfuellt',
	'kibg_einrichtung_berechtigt',
	'kibg_altersstufe',
	'kibg_hoechstbeitrag',
	'kibg_mindestbeitrag_pro_stunde',
	'kibg_subventionierte_stunden',
	'kibg_mindestbeitrag',
	'kibg_beitrag_total',
	'kibg_restkosten_eltern',
	'kibg_gesuch_innert_frist',
	'kibg_gesuch_in_uebergangsfrist',
	'kibg_beitragsbeginn',
	'kibg_beitragsbeginn_erreicht',
	'kibg_einrichtung_teilnahmebeginn',
	'kibg_verfuegung_ende',
	'kibg_verfuegung_laeuft'
];

// Datumsergebnisse: Die Web-API liefert sie als HTTP-Datum
// («Tue, 01 Aug 2028 00:00:00 GMT»); angezeigt wird JJJJ-MM-TT.
// 9999-12-31 heisst in OpenFisca «keine Angabe».
const DATUMSERGEBNISSE = [
	'kibg_beitragsbeginn',
	'kibg_einrichtung_teilnahmebeginn',
	'kibg_verfuegung_ende'
];
const isoDatum = (wert) => {
	if (!wert) return null;
	const iso = new Date(wert).toISOString().slice(0, 10);
	return iso === '9999-12-31' ? null : iso;
};

// Werte, die OpenFisca für den Haushalt berechnen soll.
const ERGEBNISSE_HAUSHALT = [
	'kibg_wohnsitz_erfuellt',
	'kibg_beschaeftigung_lit_a_erfuellt',
	'kibg_beschaeftigung_lit_b_erfuellt',
	'kibg_beschaeftigung_erfuellt',
	'kibg_massgebendes_einkommen',
	'kibg_einkommensfaktor'
];

export const ID_ELTERN = ['elternteil_1', 'elternteil_2'];
export const ID_PARTNER = 'partner';
export const idKind = (index) => `kind_${index + 1}`;

const zahl = (wert) => Number(wert);

/** Situation im Format der OpenFisca-Web-API. */
export function situation(angaben) {
	const monat = angaben.monat;
	const jahr = monat.slice(0, 4);
	const persons = {};

	angaben.eltern.forEach((person, index) => {
		const id = ID_ELTERN[index];
		persons[id] = {
			wohnsitz_kanton_sg: { [monat]: person.wohnsitz === true },
			// Eingabe in Prozent, OpenFisca rechnet mit Anteilen (80 % = 0.8).
			beschaeftigungsgrad: { [monat]: zahl(person.pensum) / 100 },
			me_steuerveranlagung: { [jahr]: zahl(person.einkommen) }
		};
		if (angaben.antragAktuell) {
			persons[id].me_aktuell = { [jahr]: zahl(person.aktuell) };
		}
		if (angaben.eltern.length === 2 && angaben.gesuchsteller === index) {
			persons[id].kibg_gesuchstellend = { [monat]: true };
		}
	});

	const mitPartner = angaben.gemeinsam === false && angaben.partner.vorhanden;
	if (mitPartner) {
		persons[ID_PARTNER] = {
			me_steuerveranlagung: { [jahr]: zahl(angaben.partner.einkommen) },
			kibg_einkommen_zaehlt_lit_b: { [monat]: null }
		};
		if (angaben.antragAktuell) {
			persons[ID_PARTNER].me_aktuell = { [jahr]: zahl(angaben.partner.aktuell) };
		}
	}

	angaben.kinder.forEach((kind, index) => {
		const ergebnisse = Object.fromEntries(ERGEBNISSE_KIND.map((n) => [n, { [monat]: null }]));
		const einrichtung = kind.typ !== 'keine';
		persons[idKind(index)] = {
			geburtsdatum: { ETERNITY: kind.geburtsdatum },
			// Art. 9 Abs. 2 KiBG, Art. 25 KiBV: Pflichtangaben (A10: Eingang bei der Gemeinde)
			betreuungsbeginn: { ETERNITY: kind.betreuungsbeginn },
			kibg_gesuchsdatum: { ETERNITY: kind.gesuchsdatum },
			eingeschult: { [monat]: kind.eingeschult === true },
			primarschule_abgeschlossen: { [monat]: kind.primarschuleAbgeschlossen === true },
			kibg_einrichtungstyp: { [monat]: kind.typ },
			kibg_einrichtung_anerkannt: { [monat]: einrichtung && kind.anerkannt === true },
			kibg_einrichtung_angemeldet: { [monat]: einrichtung && kind.angemeldet === true },
			betreuungstage_mit_obhut: { [monat]: zahl(kind.tage) },
			betreuungsstunden: { [monat]: zahl(kind.stunden) },
			kibg_betreuungskosten: { [monat]: zahl(kind.kosten) },
			...ergebnisse
		};
		// Art. 16 Abs. 1 KiBV: freiwillig; ohne Angabe nur die zwölf Monate.
		if (kind.eingeschult !== true && kind.jahrKindergarten) {
			persons[idKind(index)].jahr_eintritt_kindergarten = {
				ETERNITY: Number(kind.jahrKindergarten)
			};
		}
		// Art. 6 KiBV: freiwillig; hat Vorrang vor «angemeldet».
		if (einrichtung && kind.bestaetigtAm) {
			persons[idKind(index)].kibg_einrichtung_bestaetigt_am = { ETERNITY: kind.bestaetigtAm };
		}
	});

	const familie = {
		erziehungsberechtigte: ID_ELTERN.slice(0, angaben.eltern.length),
		kinder: angaben.kinder.map((_, index) => idKind(index)),
		gemeinsamer_haushalt: { [monat]: angaben.gemeinsam === true },
		kibg_ausnahme_bewilligt: { [monat]: angaben.ausnahme === true },
		kibg_antrag_aktuelle_gegebenheiten: { [jahr]: angaben.antragAktuell === true },
		...Object.fromEntries(ERGEBNISSE_HAUSHALT.map((n) => [n, { [monat]: null }]))
	};
	if (mitPartner) {
		familie.partner = [ID_PARTNER];
		familie.verheiratet_oder_eingetragen = { [monat]: angaben.partner.verheiratet === true };
		if (angaben.partner.verheiratet !== true && angaben.partner.seit) {
			familie.beginn_gemeinsamer_haushalt = { ETERNITY: angaben.partner.seit };
		}
	}

	return { persons, households: { familie } };
}

/** Liest die berechneten Werte für den gewählten Monat aus der Antwort. */
export function ergebnisse(antwort, angaben) {
	const monat = angaben.monat;
	const wert = (eintrag, name) => eintrag[name]?.[monat];
	const familie = antwort.households.familie;

	const haushalt = Object.fromEntries(ERGEBNISSE_HAUSHALT.map((n) => [n, wert(familie, n)]));
	const kinder = angaben.kinder.map((_, index) => {
		const person = antwort.persons[idKind(index)];
		return Object.fromEntries(
			ERGEBNISSE_KIND.map((n) => [
				n,
				DATUMSERGEBNISSE.includes(n) ? isoDatum(wert(person, n)) : wert(person, n)
			])
		);
	});
	const partner = antwort.persons[ID_PARTNER];
	return {
		haushalt,
		kinder,
		partnerEinkommenZaehlt: partner ? wert(partner, 'kibg_einkommen_zaehlt_lit_b') : null
	};
}

/**
 * Macht aus einem OpenFisca-Fehler (Status 400) eine Liste mit Feld und
 * Meldung, z. B. households/familie/gemeinsamer_haushalt.
 */
export function fehlerliste(fehler, pfad = []) {
	if (typeof fehler === 'string') {
		return [{ pfad: pfad.join('/'), meldung: fehler }];
	}
	if (fehler && typeof fehler === 'object') {
		return Object.entries(fehler).flatMap(([schluessel, wert]) =>
			fehlerliste(wert, [...pfad, schluessel])
		);
	}
	return [];
}
