// Setzt die Werte von OpenFisca in die Texte aus texte.de.json ein und
// entscheidet, welche Texte erscheinen. Jede Bedingung entspricht dem Feld
// «wann» in texte.de.json und prüft nur Werte, die OpenFisca liefert.

import texte from '#lib/texte.de.json';

export { texte };

const tausender = (ganz) => ganz.replace(/\B(?=(\d{3})+(?!\d))/g, "'");

const FORMATE = {
	// 1040 → 1'040.00
	franken: (wert) => {
		const [ganz, rappen] = Number(wert).toFixed(2).split('.');
		return `${tausender(ganz)}.${rappen}`;
	},
	// 4.125 → 4.125, 5.5 → 5.50 (Beitrag je Stunde ist nicht gerundet)
	franken_genau: (wert) => {
		const text = String(Number(Number(wert).toFixed(3)));
		const [ganz, teil = ''] = text.split('.');
		return `${tausender(ganz)}.${teil.padEnd(2, '0')}`;
	},
	// 0.5 → 50 %, 0.912 → 91.2 %
	prozent: (wert) => `${Number((Number(wert) * 100).toFixed(1))} %`,
	stunden: (wert) => String(Number(Number(wert).toFixed(2))),
	ganzzahl: (wert) => String(Math.round(Number(wert))),
	datum: (wert) => wert.split('-').reverse().join('.')
};

function formatieren(name, wert) {
	const anzeige = texte.anzeigewerte[name];
	if (anzeige) return anzeige[wert] ?? wert;
	const format = texte.formate.variablen[name];
	return format && FORMATE[format] ? FORMATE[format](wert) : String(wert);
}

/** Ersetzt {name} im Text durch den formatierten Wert. */
export function einsetzen(text, werte) {
	return text.replace(/\{([a-z_0-9]+)\}/g, (ganz, name) =>
		name in werte ? formatieren(name, werte[name]) : ganz
	);
}

const fast = (a, b) => Math.abs(Number(a) - Number(b)) < 0.005;

/** Welcher Ergebnistext für ein Kind gilt (texte.ergebnis). */
export function ergebnisArt(kind) {
	if (!kind.kibg_anspruch) return 'kein_anspruch';
	if (Number(kind.kibg_hoechstbeitrag) === 0) return 'anspruch_ohne_ansatz';
	if (Number(kind.kibg_beitrag_total) === 0) return 'anspruch_einkommen';
	return 'anspruch';
}

/** Liste der Voraussetzungen mit «erfüllt» oder «nicht erfüllt». */
export function voraussetzungen(kind, haushalt, angaben) {
	const t = texte.voraussetzungen;
	const zeile = (schluessel, erfuellt) => ({
		artikel: t[schluessel].artikel,
		erfuellt,
		text: erfuellt ? t[schluessel].erfuellt : t[schluessel].nicht_erfuellt
	});
	const liste = [
		zeile('kibg_wohnsitz_erfuellt', haushalt.kibg_wohnsitz_erfuellt),
		zeile('kibg_beschaeftigung_lit_a_erfuellt', haushalt.kibg_beschaeftigung_lit_a_erfuellt)
	];
	if (angaben.gemeinsam === true) {
		liste.push(
			zeile('kibg_beschaeftigung_lit_b_erfuellt', haushalt.kibg_beschaeftigung_lit_b_erfuellt)
		);
	}
	if (!haushalt.kibg_beschaeftigung_erfuellt && angaben.ausnahme === true) {
		liste.push(zeile('kibg_ausnahme_bewilligt', true));
	}
	liste.push(zeile('kibg_alter_erfuellt', kind.kibg_alter_erfuellt));
	liste.push(zeile('kibg_einrichtung_berechtigt', kind.kibg_einrichtung_berechtigt));
	// Art. 9 Abs. 2 KiBG, Art. 25 KiBV: vor dem Beitragsbeginn kein Beitrag.
	if (kind.kibg_beitragsbeginn) {
		liste.push(zeile('kibg_beitragsbeginn_erreicht', kind.kibg_beitragsbeginn_erreicht));
	}
	return liste;
}

/** Schritte des Rechenwegs, die für dieses Kind gelten. */
export function rechenweg(kind, eingabe) {
	return texte.rechenweg.schritte.filter((schritt) => {
		if (!schritt.wann) return true;
		// Stundengrenze greift (Art. 14 Abs. 4 KiBV)
		if (schritt.wann.startsWith('kibg_subventionierte_stunden')) {
			return Number(kind.kibg_subventionierte_stunden) < Number(eingabe.stunden);
		}
		// Kostengrenze greift (Art. 6 Abs. 2 und Art. 20 Abs. 3 KiBG)
		if (schritt.wann.startsWith('kibg_beitrag_total')) {
			return fast(kind.kibg_beitrag_total, eingabe.kosten);
		}
		return true;
	});
}

/** Hinweise, die für dieses Kind gelten. */
export function hinweise(kind, haushalt, angaben, partnerEinkommenZaehlt) {
	const h = texte.hinweise;
	const liste = [];
	if (kind.kibg_anspruch && kind.kibg_altersstufe === 'unter_18_monate') {
		liste.push(h.altersgrenze_18_monate);
	}
	if (kind.kibg_anspruch) liste.push(h.neuberechnung_25_prozent);
	if (!haushalt.kibg_beschaeftigung_erfuellt && angaben.ausnahme !== true) {
		liste.push(h.entbindung_moeglich);
	}
	if (partnerEinkommenZaehlt === true) liste.push(h.partner_einkommen_zaehlt);
	if (partnerEinkommenZaehlt === false) liste.push(h.partner_einkommen_zaehlt_nicht);
	// Datumsregeln (Art. 9 Abs. 2 KiBG, Art. 25 und Art. 6 KiBV)
	const monatsbeginn = `${angaben.monat}-01`;
	if (
		kind.kibg_anspruch &&
		kind.kibg_beitragsbeginn > monatsbeginn &&
		kind.kibg_beitragsbeginn.startsWith(angaben.monat)
	) {
		liste.push(h.beitragsbeginn_im_monat);
	}
	if (kind.kibg_gesuch_in_uebergangsfrist) liste.push(h.uebergangsfrist);
	else if (kind.kibg_gesuch_innert_frist === false) liste.push(h.gesuch_zu_spaet);
	if (kind.kibg_einrichtung_teilnahmebeginn && !kind.kibg_einrichtung_berechtigt) {
		liste.push(h.teilnahme_einrichtung);
	}
	if (kind.kibg_anspruch) {
		liste.push(h.gesuchsfrist_30_tage);
		liste.push(h.meldepflicht);
	}
	return liste;
}
