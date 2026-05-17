const API_BASE = 'http://127.0.0.1:8047/api';

async function fetchApi<T>(path: string): Promise<T> {
	const res = await fetch(`${API_BASE}${path}`);
	if (!res.ok) {
		throw new Error(`API error: ${res.status}`);
	}
	return res.json();
}

export interface Groupe {
	id: number;
	slug: string;
	nom: string;
	acronyme: string;
	couleur: string | null;
}

export interface DeputeListItem {
	uid: string;
	slug: string;
	nom: string;
	prenom: string;
	circo_departement: string | null;
	circo_numero: number | null;
	photo_url: string | null;
	groupe: Groupe | null;
}

export interface DeputeVote {
	position: string;
	scrutin_numero: number;
	scrutin_titre: string;
	scrutin_date: string;
	scrutin_sort: string;
}

export interface DeputeDetail extends DeputeListItem {
	sexe: string | null;
	date_naissance: string | null;
	date_mandat_debut: string | null;
	url_an: string | null;
	recent_votes: DeputeVote[];
}

export interface ScrutinListItem {
	id: number;
	numero: number;
	titre: string;
	date_scrutin: string;
	sort: string;
	nb_pour: number;
	nb_contre: number;
	nb_abstention: number;
	nb_votants: number;
}

export interface VoteOut {
	position: string;
	depute_uid: string;
	depute_nom: string;
	depute_prenom: string;
	groupe_acronyme: string | null;
}

export interface ScrutinDetail extends ScrutinListItem {
	votes: VoteOut[];
}

export interface Stats {
	total_deputes: number;
	total_groupes: number;
	total_scrutins: number;
	total_votes: number;
	derniere_sync: string | null;
}

export interface SearchResult {
	deputes: DeputeListItem[];
	scrutins: ScrutinListItem[];
}

export function getDeputes(params?: { page?: number; groupe?: string; search?: string }) {
	const query = new URLSearchParams();
	if (params?.page) query.set('page', String(params.page));
	if (params?.groupe) query.set('groupe', params.groupe);
	if (params?.search) query.set('search', params.search);
	const qs = query.toString();
	return fetchApi<DeputeListItem[]>(`/deputes${qs ? '?' + qs : ''}`);
}

export function getDepute(uid: string) {
	return fetchApi<DeputeDetail>(`/deputes/${uid}`);
}

export function getScrutins(params?: { page?: number; sort?: string }) {
	const query = new URLSearchParams();
	if (params?.page) query.set('page', String(params.page));
	if (params?.sort) query.set('sort', params.sort);
	const qs = query.toString();
	return fetchApi<ScrutinListItem[]>(`/scrutins${qs ? '?' + qs : ''}`);
}

export function getScrutin(numero: number) {
	return fetchApi<ScrutinDetail>(`/scrutins/${numero}`);
}

export function getGroupes() {
	return fetchApi<Groupe[]>('/groupes');
}

export function search(q: string) {
	return fetchApi<SearchResult>(`/search?q=${encodeURIComponent(q)}`);
}

export function getStats() {
	return fetchApi<Stats>('/stats');
}
