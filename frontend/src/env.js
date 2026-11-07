import { defineEnvVars } from '@sveltejs/kit/env';

export const variables = defineEnvVars({
	OPENFISCA_URL: {
		description: 'Adresse der OpenFisca-Web-API (make serve-local im Ordner openfisca-CH-SG)',
		// Ohne Angabe: die lokale OpenFisca-API.
		schema: (wert) => wert || 'http://127.0.0.1:5000'
	}
});
