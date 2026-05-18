<script lang="ts">
	import { onMount } from 'svelte';
	import { getDeputes, getGroupes, type DeputeListItem, type Groupe } from '$lib/api';

	let deputes = $state<DeputeListItem[]>([]);
	let groupes = $state<Groupe[]>([]);
	let selectedGroupe = $state('');
	let searchText = $state('');
	let page = $state(1);
	let loading = $state(true);

	async function load() {
		loading = true;
		try {
			deputes = await getDeputes({
				page,
				groupe: selectedGroupe || undefined,
				search: searchText || undefined
			});
		} catch {
			deputes = [];
		}
		loading = false;
	}

	onMount(async () => {
		groupes = await getGroupes();
		await load();
	});

	function handleFilter() {
		page = 1;
		load();
	}
</script>

<svelte:head>
	<title>Deputes — Hemicycle</title>
</svelte:head>

<h1>Deputes</h1>

<div class="filters">
	<input
		type="text"
		placeholder="Rechercher un depute..."
		bind:value={searchText}
		oninput={handleFilter}
		aria-label="Rechercher un depute"
	/>
	<select bind:value={selectedGroupe} onchange={handleFilter} aria-label="Filtrer par groupe">
		<option value="">Tous les groupes</option>
		{#each groupes as g}
			<option value={g.acronyme}>{g.acronyme} — {g.nom}</option>
		{/each}
	</select>
</div>

{#if loading}
	<p class="loading">Chargement...</p>
{:else if deputes.length === 0}
	<p class="empty">Aucun depute trouve.</p>
{:else}
	<div class="deputes-grid">
		{#each deputes as d}
			<a href="/depute/{d.uid}" class="depute-card card">
				<img
					src={d.photo_url || ''}
					alt="{d.prenom} {d.nom}"
					class="photo"
					loading="lazy"
					onerror={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
				/>
				<div class="info">
					<strong>{d.prenom} {d.nom}</strong>
					{#if d.groupe}
						<span class="badge">{d.groupe.acronyme}</span>
					{/if}
					{#if d.circo_departement}
						<span class="circo">{d.circo_departement} ({d.circo_numero})</span>
					{/if}
				</div>
			</a>
		{/each}
	</div>

	<div class="pagination">
		{#if page > 1}
			<button onclick={() => { page--; load(); }}>Precedent</button>
		{/if}
		<span>Page {page}</span>
		{#if deputes.length === 50}
			<button onclick={() => { page++; load(); }}>Suivant</button>
		{/if}
	</div>
{/if}

<style>
	h1 {
		margin-bottom: 1.5rem;
	}

	.filters {
		display: flex;
		gap: 1rem;
		margin-bottom: 1.5rem;
		flex-wrap: wrap;
	}

	.filters input {
		flex: 1;
		min-width: 200px;
	}

	.filters select {
		min-width: 200px;
	}

	.deputes-grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
		gap: 0.75rem;
	}

	.depute-card {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		color: var(--text);
	}

	.depute-card:hover {
		text-decoration: none;
	}

	.photo {
		width: 48px;
		height: 56px;
		object-fit: cover;
		background: var(--rule);
	}

	.info {
		display: flex;
		flex-direction: column;
		gap: 0.15rem;
	}

	.info .badge {
		font-size: 0.75rem;
		color: var(--accent);
	}

	.circo {
		font-size: 0.8rem;
		color: var(--text-muted);
	}

	.pagination {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 1rem;
		margin-top: 2rem;
	}

	.pagination button {
		background: var(--paper);
		color: var(--ink);
		border: 1px solid var(--rule);
		padding: 0.5rem 1rem;
		cursor: pointer;
	}

	.pagination button:hover {
		background: var(--bg-hover);
	}

	.loading, .empty {
		text-align: center;
		color: var(--text-muted);
		padding: 2rem;
	}
</style>
