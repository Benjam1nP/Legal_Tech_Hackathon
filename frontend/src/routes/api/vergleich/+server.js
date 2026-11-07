import { json } from '@sveltejs/kit';
import { OPENFISCA_URL } from '$app/env/private';
import { fehlerliste } from '#lib/server/situation.js';
import { auswerten, faelle, situation } from '#lib/server/vergleich.js';

// Vergleich im Dashboard: rechnet alle Kombinationen aus Pensum, Betreuungsform
// und Ansicht in einer Anfrage mit OpenFisca. Die Angaben werden nicht
// gespeichert.
export async function POST({ request, fetch }) {
	const angaben = await request.json();
	const liste = faelle(angaben);

	let antwort;
	try {
		antwort = await fetch(`${OPENFISCA_URL}/calculate`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(situation(angaben, liste))
		});
	} catch {
		return json(
			{ fehler: [{ pfad: '', meldung: 'Die Berechnung ist im Moment nicht erreichbar.' }] },
			{ status: 503 }
		);
	}

	const inhalt = await antwort.json();
	if (!antwort.ok) {
		return json({ fehler: fehlerliste(inhalt) }, { status: antwort.status });
	}
	return json(auswerten(inhalt, angaben, liste));
}
