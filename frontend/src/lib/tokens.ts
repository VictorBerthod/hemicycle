/**
 * Design tokens — [PROJET]
 * Source : design_handoff_nsv_politique/README.md §5
 *
 * Les couleurs CSS de surface/texte vivent dans app.css (variables CSS).
 * Ce fichier expose les tokens consommés en JS/TS : couleurs par groupe
 * politique, ordre du spectre, helpers de position de vote.
 */

export type VotePosition = 'pour' | 'contre' | 'abst' | 'absent';

/**
 * Couleur par groupe parlementaire (acronyme officiel ou variante).
 * Couvre les groupes actuels de l'AN et inclut les synonymes utilisés
 * dans les données amont (LFI vs LFI-NFP, EPR vs RE, etc.).
 */
export const GROUP_COLORS: Record<string, string> = {
	LFI: '#c12c44',
	'LFI-NFP': '#c12c44',
	GDR: '#a31822',
	PCF: '#a31822',
	ECOS: '#3b8e54',
	EELV: '#3b8e54',
	SOC: '#e88a8a',
	PS: '#e88a8a',
	LIOT: '#2a8e9b',
	DEM: '#e69220',
	EPR: '#d9b438',
	RE: '#d9b438',
	HOR: '#3aa3c9',
	DR: '#2a5fa6',
	LR: '#2a5fa6',
	UDR: '#1f4280',
	UDDPLR: '#1f4280',
	RN: '#0d2f6e',
	NI: '#888888',
};

/**
 * Ordre du spectre politique gauche → droite.
 * Utilisé pour trier les groupes dans l'hémicycle et les légendes.
 */
export const SPECTRUM = [
	'LFI',
	'GDR',
	'ECOS',
	'SOC',
	'LIOT',
	'DEM',
	'EPR',
	'HOR',
	'DR',
	'UDR',
	'RN',
	'NI',
] as const;

/**
 * Retourne la variable CSS de couleur pour une position de vote.
 * Utiliser via `style="background: var(${getVoteColorVar(position)})"`.
 */
export function getVoteColorVar(position: VotePosition): string {
	switch (position) {
		case 'pour':
			return '--pour';
		case 'contre':
			return '--contre';
		case 'abst':
			return '--abst';
		case 'absent':
			return '--absent';
	}
}

/**
 * Normalise une position venue de l'API (legacy : "abstention", "non_votant", etc.)
 * vers la forme canonique du frontend ('pour'|'contre'|'abst'|'absent').
 */
export function normalizePosition(raw: string): VotePosition {
	const v = raw.toLowerCase();
	if (v === 'pour' || v === 'for') return 'pour';
	if (v === 'contre' || v === 'against') return 'contre';
	if (v.startsWith('abst')) return 'abst';
	return 'absent';
}

/**
 * Trie une liste de groupes selon l'ordre du spectre politique.
 * Les acronymes inconnus sont placés en fin.
 */
export function sortBySpectrum<T extends { acronyme: string }>(groups: T[]): T[] {
	const order = (acro: string): number => {
		const direct = SPECTRUM.indexOf(acro as (typeof SPECTRUM)[number]);
		if (direct !== -1) return direct;
		// Synonymes : tenter via la couleur partagée
		const color = GROUP_COLORS[acro];
		if (!color) return 99;
		for (let i = 0; i < SPECTRUM.length; i++) {
			if (GROUP_COLORS[SPECTRUM[i]] === color) return i;
		}
		return 99;
	};
	return [...groups].sort((a, b) => order(a.acronyme) - order(b.acronyme));
}

/**
 * Renvoie la couleur d'un groupe avec fallback gris si inconnu.
 */
export function getGroupColor(acronyme: string): string {
	return GROUP_COLORS[acronyme] ?? '#888888';
}
