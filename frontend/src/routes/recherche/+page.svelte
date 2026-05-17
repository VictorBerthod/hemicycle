<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { search, type SearchResult } from '$lib/api';

	let results = $state<SearchResult | null>(null);
	let loading = $state(true);
	let query = $derived($page.url.searchParams.get('q') || '');

	onMount(async () => {
		if (query.length >= 2) {
			try {
				results = await search(query);
			} catch {
				results = { deputes: [], scrutins: [] };
			}
		}
		loading = false;
	});
</script>

<svelte:head>
	<title>Recherche "{query}" — Hemicycle</title>
</svelte:head>

<h1>Recherche : "{query}"</h1>

{#if loading}
	<p class="loading">Chargement...</p>
{:else if results}
	{#if results.deputes.length > 0}
		<section>
			<h2>Deputes ({results.deputes.length})</h2>
			<ul class="results-list">
				{#each results.deputes as d}
					<li class="card">
						<a href="/depute/{d.uid}">{d.prenom} {d.nom}</a>
						{#if d.groupe}
							<span class="tag">{d.groupe.acronyme}</span>
						{/if}
					</li>
				{/each}
			</ul>
		</section>
	{/if}

	{#if results.scrutins.length > 0}
		<section>
			<h2>Scrutins ({results.scrutins.length})</h2>
			<ul class="results-list">
				{#each results.scrutins as s}
					<li class="card">
						<a href="/scrutin/{s.numero}">{s.titre}</a>
						<span class="meta">{s.date_scrutin} — <span class="badge badge-{s.sort}">{s.sort}</span></span>
					</li>
				{/each}
			</ul>
		</section>
	{/if}

	{#if results.deputes.length === 0 && results.scrutins.length === 0}
		<p class="empty">Aucun resultat pour "{query}".</p>
	{/if}
{/if}

<style>
	h1 { margin-bottom: 1.5rem; }
	h2 { margin: 1.5rem 0 0.75rem; }

	.results-list {
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.results-list li {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.tag {
		font-size: 0.8rem;
		color: var(--accent);
	}

	.meta {
		font-size: 0.8rem;
		color: var(--text-muted);
	}

	.loading, .empty {
		text-align: center;
		color: var(--text-muted);
		padding: 2rem;
	}
</style>
