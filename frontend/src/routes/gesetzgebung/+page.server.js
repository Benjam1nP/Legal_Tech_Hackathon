import { KIBG_HTML, KIBV_HTML } from '#lib/server/recht.js';

export function load() {
	return { kibg: KIBG_HTML, kibv: KIBV_HTML };
}
