<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { getDeputes, getGroupes, type DeputeListItem, type Groupe } from '$lib/api';
	import { getGroupColor } from '$lib/tokens';
	import Eyebrow from '$lib/components/Eyebrow.svelte';
	import Mono from '$lib/components/Mono.svelte';
	import Placeholder from '$lib/components/Placeholder.svelte';

	const LIMIT = 24;

	let deputes = $state<DeputeListItem[]>([]);
	let groupes = $state<Groupe[]>([]);
	let total = $state(0);
	let loading = $state(true);
	let error = $state('');

	let currentPage = $state(1);
	let selectedGroupe = $state<string>('');
	let searchQuery = $state('');

	// Sync URL params → state on mount
	onMount(async () => {
		selectedGroupe = page.url.searchParams.get('groupe') ?? '';
		currentPage = parseInt(page.url.searchParams.get('page') ?? '1', 10);

		try {
			const [g] = await Promise.all([getGroupes()]);
			groupes = g;
		} catch {
			error = 'Impossible de charger les données.';
		}

		await loadDeputes();
	});

	async function loadDeputes() {
		loading = true;
		try {
			const data = await getDeputes({
				page: currentPage,
				groupe: selectedGroupe || undefined,
				search: searchQuery || undefined,
			});
			deputes = data;
			// Estimate total from page size (simple heuristic — no total returned by API)
			total = data.length === LIMIT ? currentPage * LIMIT + 1 : (currentPage - 1) * LIMIT + data.length;
		} catch {
			error = 'Impossible de charger les députés.';
		} finally {
			loading = false;
		}
	}

	async function applyGroupe(acronyme: string) {
		selectedGroupe = selectedGroupe === acronyme ? '' : acronyme;
		currentPage = 1;
		await loadDeputes();
		goto(`/personnalites?groupe=${selectedGroupe}&page=1`, { replaceState: true, noScroll: true });
	}

	async function applySearch(e: Event) {
		searchQuery = (e.target as HTMLInputElement).value;
		currentPage = 1;
		await loadDeputes();
	}

	async function goPage(p: number) {
		currentPage = p;
		await loadDeputes();
		window.scrollTo({ top: 0, behavior: 'smooth' });
	}

	async function reset() {
		selectedGroupe = '';
		searchQuery = '';
		currentPage = 1;
		await loadDeputes();
		goto('/personnalites', { replaceState: true, noScroll: true });
	}

	let totalPages = $derived(Math.max(1, Math.ceil(total / LIMIT)));
</script>

<svelte:head>
	<title>Annuaire des personnalités — [PROJET].fr</title>
</svelte:head>

<!-- ── HEADER ─────────────────────────────────────────────────────────────── -->
<header class="ann-header">
	<Eyebrow>Personnalités · Assemblée nationale · 17ᵉ législature</Eyebrow>
	<div class="ann-title-row">
		<h1>577 députées et députés,<br/><em>une fiche par voix</em>.</h1>
		<div class="ann-kpis">
			<div class="kpi">
				<span class="kpi-num">577</span>
				<Mono>députés</Mono>
			</div>
			<div class="kpi">
				<span class="kpi-num">87%</span>
				<Mono>participation moy.</Mono>
			</div>
			<div class="kpi accent">
				<span class="kpi-num">314</span>
				<Mono>écarts documentés</Mono>
			</div>
		</div>
	</div>
</header>

<!-- ── CORPS ──────────────────────────────────────────────────────────────── -->
<div class="ann-body">

	<!-- Sidebar -->
	<aside class="sidebar">
		<!-- Search -->
		<div class="search-box">
			<span class="search-icon" aria-hidden="true">⌕</span>
			<input
				type="search"
				placeholder="Rechercher un nom…"
				bind:value={searchQuery}
				oninput={applySearch}
				aria-label="Rechercher un député par nom"
			/>
		</div>

		<!-- Groupes -->
		{#if groupes.length > 0}
		<div class="filter-group">
			<Mono color="var(--ink)">Groupe parlementaire</Mono>
			<ul class="filter-list">
				{#each groupes as g (g.id)}
					<li>
						<button
							class="filter-item"
							class:active={selectedGroupe === g.acronyme}
							onclick={() => applyGroupe(g.acronyme)}
						>
							<span class="check" aria-hidden="true">{selectedGroupe === g.acronyme ? '✓' : ''}</span>
							<span class="groupe-dot" style:background={getGroupColor(g.acronyme)}></span>
							<span class="filter-label" class:active={selectedGroupe === g.acronyme}>{g.acronyme}</span>
							<Mono>{g.nom.length > 20 ? g.nom.slice(0, 20) + '…' : g.nom}</Mono>
						</button>
					</li>
				{/each}
			</ul>
		</div>
		{/if}

		<button class="reset-btn" onclick={reset} type="button">
			Réinitialiser les filtres
		</button>
	</aside>

	<!-- Grille -->
	<div class="grid-zone">
		<!-- Compteur + tri -->
		<div class="grid-topbar">
			<p class="result-count">
				<strong>{deputes.length}</strong> personnalités correspondent à vos filtres
			</p>
			<div class="sort-row">
				<Mono>Trier :</Mono>
				<button class="sort-btn active" type="button">nom A→Z</button>
				<button class="sort-btn" type="button">écarts ↓</button>
			</div>
		</div>

		{#if error}
			<p class="error-msg">{error}</p>
		{/if}

		<!-- Cards -->
		{#if loading}
			<div class="cards-grid">
				{#each Array(9) as _}
					<div class="person-card skeleton">
						<Placeholder width="64px" height="72px" />
						<div class="card-info">
							<Placeholder width="80%" height="18px" />
							<Placeholder width="60%" height="12px" />
						</div>
					</div>
				{/each}
			</div>
		{:else if deputes.length === 0}
			<div class="empty-state">
				<Mono>Aucun résultat pour ces filtres.</Mono>
			</div>
		{:else}
			<div class="cards-grid">
				{#each deputes as d (d.uid)}
					<a href="/personnalite/{d.uid}" class="person-card">
						{#if d.photo_url}
							<img src={d.photo_url} alt="{d.prenom} {d.nom}" class="person-photo" />
						{:else}
							<div class="person-photo placeholder-photo" aria-hidden="true"></div>
						{/if}
						<div class="card-info">
							<div class="card-name-row">
								<h4>{d.prenom} {d.nom}</h4>
								{#if d.groupe}
									<span
										class="groupe-tag"
										style:color={getGroupColor(d.groupe.acronyme)}
										style:border-left="2px solid {getGroupColor(d.groupe.acronyme)}"
									>{d.groupe.acronyme}</span>
								{/if}
							</div>
							{#if d.circo_departement}
								<Mono>{d.circo_departement}{d.circo_numero ? ` · ${d.circo_numero}ᵉ` : ''}</Mono>
							{/if}
						</div>
					</a>
				{/each}
			</div>

			<!-- Pagination -->
			{#if totalPages > 1}
			<div class="pagination">
				<Mono>Page {currentPage} sur {totalPages}</Mono>
				<div class="page-btns">
					<button
						class="page-btn"
						disabled={currentPage === 1}
						onclick={() => goPage(currentPage - 1)}
					>‹</button>
					{#each Array.from({ length: Math.min(totalPages, 7) }, (_, i) => i + 1) as p (p)}
						<button
							class="page-btn"
							class:active={p === currentPage}
							onclick={() => goPage(p)}
						>{p}</button>
					{/each}
					<button
						class="page-btn"
						disabled={currentPage === totalPages}
						onclick={() => goPage(currentPage + 1)}
					>›</button>
				</div>
			</div>
			{/if}
		{/if}
	</div>
</div>

<style>
	/* ── Header ───────────────────────────────────────────────────────── */
	.ann-header {
		padding: 40px var(--page-pad-x) 28px;
		border-bottom: 1px solid var(--ink);
	}

	.ann-title-row {
		display: flex;
		align-items: baseline;
		justify-content: space-between;
		gap: 32px;
		margin-top: 14px;
	}

	.ann-header h1 {
		font-size: clamp(32px, 5vw, 64px);
		font-weight: 400;
		line-height: 0.95;
		letter-spacing: -0.025em;
		margin: 0;
	}

	.ann-header h1 em {
		color: var(--accent);
		font-style: italic;
	}

	.ann-kpis {
		display: flex;
		gap: 32px;
		flex-shrink: 0;
	}

	.kpi { display: flex; flex-direction: column; align-items: flex-end; }

	.kpi-num {
		font-family: var(--font-serif);
		font-size: 36px;
		font-weight: 500;
		color: var(--ink);
		line-height: 1;
	}

	.kpi.accent .kpi-num { color: var(--accent); }

	/* ── Body layout ──────────────────────────────────────────────────── */
	.ann-body {
		display: grid;
		grid-template-columns: 260px 1fr;
		gap: 40px;
		padding: 32px var(--page-pad-x);
	}

	/* ── Sidebar ──────────────────────────────────────────────────────── */
	.sidebar {
		display: flex;
		flex-direction: column;
		gap: 22px;
	}

	.search-box {
		display: flex;
		align-items: center;
		gap: 10px;
		background: var(--paper);
		border: 1px solid var(--ink);
		padding: 10px 12px;
		font-family: var(--font-mono);
		font-size: 13px;
		color: var(--muted);
	}

	.search-icon { color: var(--ink); }

	.search-box input {
		flex: 1;
		border: none;
		outline: none;
		background: transparent;
		font-family: var(--font-mono);
		font-size: 13px;
		color: var(--ink);
	}

	.filter-group { display: flex; flex-direction: column; gap: 10px; }

	.filter-list {
		list-style: none;
		padding: 0;
		margin: 0;
		display: flex;
		flex-direction: column;
		gap: 4px;
	}

	.filter-item {
		display: flex;
		align-items: center;
		gap: 10px;
		padding: 4px 0;
		background: none;
		border: none;
		cursor: pointer;
		width: 100%;
		text-align: left;
		font-size: 14px;
		color: var(--ink);
	}

	.filter-item:hover { background: var(--bg-alt); }

	.check {
		width: 14px;
		height: 14px;
		border: 1px solid var(--ink);
		display: flex;
		align-items: center;
		justify-content: center;
		font-size: 10px;
		font-family: var(--font-mono);
		flex-shrink: 0;
		background: transparent;
	}

	.filter-item.active .check { background: var(--ink); color: var(--bg); }

	.groupe-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		flex-shrink: 0;
	}

	.filter-label { flex: 1; font-weight: 400; }
	.filter-label.active { font-weight: 600; }

	.reset-btn {
		width: 100%;
		padding: 10px 0;
		background: transparent;
		border: 1px solid var(--ink);
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		font-weight: 600;
		color: var(--muted);
		cursor: pointer;
	}

	.reset-btn:hover { background: var(--bg-alt); }

	/* ── Grid zone ────────────────────────────────────────────────────── */
	.grid-zone { min-width: 0; }

	.grid-topbar {
		display: flex;
		justify-content: space-between;
		align-items: baseline;
		margin-bottom: 16px;
	}

	.result-count {
		font-family: var(--font-serif);
		font-style: italic;
		font-size: 19px;
		color: var(--muted);
		margin: 0;
	}

	.result-count strong {
		color: var(--ink);
		font-style: normal;
		font-family: var(--font-mono);
		font-weight: 600;
		font-size: 14px;
		letter-spacing: 0.04em;
	}

	.sort-row {
		display: flex;
		align-items: center;
		gap: 10px;
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--muted);
	}

	.sort-btn {
		background: none;
		border: none;
		cursor: pointer;
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--muted);
		padding: 0;
	}

	.sort-btn.active {
		color: var(--ink);
		border-bottom: 1px solid var(--ink);
	}

	/* ── Cards ────────────────────────────────────────────────────────── */
	.cards-grid {
		display: grid;
		grid-template-columns: repeat(3, 1fr);
		gap: 16px;
	}

	.person-card {
		background: var(--paper);
		border: 1px solid var(--rule);
		display: grid;
		grid-template-columns: 64px 1fr;
		gap: 14px;
		padding: 16px;
		text-decoration: none;
		color: inherit;
		transition: border-color 0.15s;
	}

	.person-card:hover { border-color: var(--ink); }

	.person-photo {
		width: 64px;
		height: 72px;
		object-fit: cover;
		display: block;
	}

	.placeholder-photo {
		background: repeating-linear-gradient(45deg, var(--bg-alt), var(--bg-alt) 6px, #ddd8c9 6px, #ddd8c9 12px);
		border: 1px solid var(--muted);
	}

	.card-info {
		display: flex;
		flex-direction: column;
		min-width: 0;
		gap: 2px;
	}

	.card-name-row {
		display: flex;
		justify-content: space-between;
		align-items: flex-start;
		gap: 6px;
	}

	.card-info h4 {
		font-family: var(--font-serif);
		font-size: 17px;
		font-weight: 500;
		line-height: 1.1;
		margin: 0;
		color: var(--ink);
	}

	.groupe-tag {
		font-family: var(--font-mono);
		font-size: 10px;
		font-weight: 600;
		letter-spacing: 0.04em;
		padding-left: 6px;
		white-space: nowrap;
		flex-shrink: 0;
	}

	/* ── Skeleton ─────────────────────────────────────────────────────── */
	.skeleton {
		pointer-events: none;
	}

	/* ── Empty state ──────────────────────────────────────────────────── */
	.empty-state {
		padding: 60px 0;
		text-align: center;
	}

	/* ── Pagination ───────────────────────────────────────────────────── */
	.pagination {
		margin-top: 32px;
		display: flex;
		justify-content: space-between;
		align-items: center;
		padding-top: 20px;
		border-top: 1px solid var(--rule);
	}

	.page-btns {
		display: flex;
		gap: 6px;
	}

	.page-btn {
		width: 30px;
		height: 30px;
		display: flex;
		align-items: center;
		justify-content: center;
		background: transparent;
		color: var(--ink);
		border: 1px solid var(--rule);
		font-family: var(--font-mono);
		font-size: 12px;
		font-weight: 600;
		cursor: pointer;
	}

	.page-btn.active {
		background: var(--ink);
		color: var(--bg);
		border-color: var(--ink);
	}

	.page-btn:disabled { opacity: 0.3; cursor: default; }

	.error-msg {
		color: var(--contre);
		font-size: 14px;
		margin: 12px 0;
	}

	/* ── Responsive ───────────────────────────────────────────────────── */
	@media (max-width: 1024px) {
		.ann-body { grid-template-columns: 220px 1fr; gap: 24px; }
		.cards-grid { grid-template-columns: repeat(2, 1fr); }
		.ann-title-row { flex-direction: column; }
		.ann-kpis { justify-content: flex-start; }
	}

	@media (max-width: 640px) {
		.ann-body { grid-template-columns: 1fr; }
		.sidebar { display: none; }
		.cards-grid { grid-template-columns: 1fr; }
	}
</style>
