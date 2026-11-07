import adapter from '@sveltejs/adapter-node';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		sveltekit({
			// Node-Server, damit die Route /api/berechnen die OpenFisca-API aufrufen kann.
			adapter: adapter()
		})
	]
});
