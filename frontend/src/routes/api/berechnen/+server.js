import { json } from '@sveltejs/kit';
import { OPENFISCA_URL } from '$app/env/private';
import { situation, ergebnisse, fehlerliste } from '#lib/server/situation.js';

// Nimmt die Formularangaben entgegen, rechnet mit OpenFisca und gibt die
// Ergebnisse zurück. Die Angaben werden nicht gespeichert.
export async function POST({ request, fetch }) {
	const angaben = await request.json();

	let antwort;
	try {
		antwort = await fetch(`${OPENFISCA_URL}/calculate`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify(situation(angaben))
		});
	} catch {
		return json(
			{ fehler: [{ pfad: '', meldung: 'Die Berechnung ist im Moment nicht erreichbar.' }] },
			{ status: 503 }
		);
	}

	const inhalt = await antwort.json();
	if (!antwort.ok) {
		// Fehler 400: OpenFisca nennt das Feld, z. B. persons/kind_1/geburtsdatum.
		return json({ fehler: fehlerliste(inhalt) }, { status: antwort.status });
	}
	return json(ergebnisse(inhalt, angaben));
}
