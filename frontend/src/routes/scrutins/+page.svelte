<script lang="ts">
	import { onMount } from 'svelte';
	import { getScrutins, type ScrutinListItem } from '$lib/api';

	let scrutins = $state<ScrutinListItem[]>([]);
	let filterSort = $state('');
	let page = $state(1);
	let loading = $state(true);

	async function load() {
		loading = true;
		try {
			scrutins = await getScrutins({
				page,
				sort: filterSort || undefined
			});
		} catch {
			scrutins = [];
		}
		loading = false;
	}

	onMount(load);

	function handleFilter() {
		page = 1;
		load();
	}

	function voteBarStyle(s: ScrutinListItem) {
		const total = s.nb_pour + s.nb_contre + s.nb_abstention;
		if (total === 0) return '';
		const pour = (s.nb_pour / total) * 100;
		const contre = (s.nb_contre / total) * 100;
		return `pour:${pour.toFixed(1)}%;contre:${contre.toFixed(1)}%`;
	}
</script>

<svelte:head>
	<title>Scrutins — Hemicycle</title>
</svelte:head>

<h1>Scrutins</h1>

<div class="filters">
	<select bind:value={filterSort} onchange={handleFilter} aria-label="Filtrer par resultat">
		<option value="">Tous les resultats</option>
		<option value="adopte">Adoptes</option>
		<option value="rejete">Rejetes</option>
	</select>
</div>

{#if loading}
	<p class="loading">Chargement...</p>
{:else if scrutins.length === 0}
	<p class="empty">Aucun scrutin trouve.</p>
{:else}
	<ul class="scrutins-list">
		{#each scrutins as s}
			<li>
				<a href="/scrutin/{s.numero}" class="card scrutin-card">
					<div class="scrutin-header">
						<span class="scrutin-date">{s.date_scrutin}</span>
						<span class="badge badge-{s.sort}">{s.sort}</span>
					</div>
					<p class="scrutin-titre">{s.titre}</p>
					{#if s.nb_votants > 0}
						<div class="vote-bar" role="img" aria-label="{s.nb_pour} pour, {s.nb_contre} contre, {s.nb_abstention} abstentions">
							<div class="pour" style="width: {(s.nb_pour / (s.nb_pour + s.nb_contre + s.nb_abstention)) * 100}%"></div>
							<div class="contre" style="width: {(s.nb_contre / (s.nb_pour + s.nb_contre + s.nb_abstention)) * 100}%"></div>
							<div class="abstention" style="width: {(s.nb_abstention / (s.nb_pour + s.nb_contre + s.nb_abstention)) * 100}%"></div>
						</div>
						<div class="vote-counts">
							<span class="count-pour">{s.nb_pour} pour</span>
							<span class="count-contre">{s.nb_contre} contre</span>
							<span class="count-abstention">{s.nb_abstention} abst.</span>
						</div>
					{/if}
				</a>
			</li>
		{/each}
	</ul>

	<div class="pagination">
		{#if page > 1}
			<button onclick={() => { page--; load(); }}>Precedent</button>
		{/if}
		<span>Page {page}</span>
		{#if scrutins.length === 20}
			<button onclick={() => { page++; load(); }}>Suivant</button>
		{/if}
	</div>
{/if}

<style>
	h1 { margin-bottom: 1.5rem; }

	.filters { margin-bottom: 1.5rem; }

	.scrutins-list {
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.scrutin-card {
		display: block;
		color: var(--text);
	}

	.scrutin-card:hover { text-decoration: none; }

	.scrutin-header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		margin-bottom: 0.5rem;
	}

	.scrutin-date {
		font-size: 0.85rem;
		color: var(--text-muted);
	}

	.scrutin-titre {
		font-size: 0.95rem;
		margin-bottom: 0.5rem;
	}

	.vote-counts {
		display: flex;
		gap: 1rem;
		font-size: 0.8rem;
		margin-top: 0.35rem;
	}

	.count-pour { color: var(--pour); }
	.count-contre { color: var(--contre); }
	.count-abstention { color: var(--abstention); }

	.pagination {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 1rem;
		margin-top: 2rem;
	}

	.pagination button {
		background: var(--bg-card);
		color: var(--text);
		border: 1px solid var(--border);
		padding: 0.5rem 1rem;
		border-radius: var(--radius);
		cursor: pointer;
	}

	.loading, .empty {
		text-align: center;
		color: var(--text-muted);
		padding: 2rem;
	}
</style>
