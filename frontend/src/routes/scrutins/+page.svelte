<script lang="ts">
	import { onMount } from 'svelte';
	import { getScrutins, type ScrutinListItem } from '$lib/api';
	import VoteBadge from '$lib/components/VoteBadge.svelte';
	import VoteBar from '$lib/components/VoteBar.svelte';

	let scrutins = $state<ScrutinListItem[]>([]);
	let filterSort = $state('');
	let currentPage = $state(1);
	let loading = $state(true);

	async function load() {
		loading = true;
		try {
			scrutins = await getScrutins({ page: currentPage, sort: filterSort || undefined });
		} catch {
			scrutins = [];
		}
		loading = false;
	}

	onMount(load);

	function handleFilter() {
		currentPage = 1;
		load();
	}
</script>

<svelte:head>
	<title>Scrutins — [PROJET].fr</title>
</svelte:head>

<div class="page-wrap">
	<h1>Scrutins</h1>

	<div class="filters">
		<select bind:value={filterSort} onchange={handleFilter} aria-label="Filtrer par résultat">
			<option value="">Tous les résultats</option>
			<option value="adopte">Adoptés</option>
			<option value="rejete">Rejetés</option>
		</select>
	</div>

	{#if loading}
		<p class="loading">Chargement…</p>
	{:else if scrutins.length === 0}
		<p class="empty">Aucun scrutin trouvé.</p>
	{:else}
		<table class="scrutins-table">
			<thead>
				<tr>
					{#each ['n°', 'Titre', 'Date', 'Résultat', 'Répartition', 'Pour', 'Contre', 'Abst.'] as h (h)}
						<th>{h}</th>
					{/each}
				</tr>
			</thead>
			<tbody>
				{#each scrutins as s (s.id)}
					<tr>
						<td class="num"><a href="/scrutin/{s.numero}">n°{s.numero}</a></td>
						<td class="titre"><a href="/scrutin/{s.numero}">{s.titre}</a></td>
						<td class="date">{s.date_scrutin}</td>
						<td><VoteBadge position={s.sort === 'adopte' ? 'adopte' : 'rejete'} /></td>
						<td class="bar-cell"><VoteBar pour={s.nb_pour} contre={s.nb_contre} abst={s.nb_abstention} /></td>
						<td class="vote-num pour">{s.nb_pour}</td>
						<td class="vote-num contre">{s.nb_contre}</td>
						<td class="vote-num abst">{s.nb_abstention}</td>
					</tr>
				{/each}
			</tbody>
		</table>

		<div class="pagination">
			{#if currentPage > 1}
				<button onclick={() => { currentPage--; load(); }}>Précédent</button>
			{/if}
			<span>Page {currentPage}</span>
			{#if scrutins.length === 20}
				<button onclick={() => { currentPage++; load(); }}>Suivant</button>
			{/if}
		</div>
	{/if}
</div>

<style>
	.page-wrap { padding: 32px var(--page-pad-x); }

	h1 { margin-bottom: 1.5rem; }

	.filters { margin-bottom: 1.5rem; }

	.scrutins-table {
		width: 100%;
		border-collapse: collapse;
		font-size: 15px;
	}

	.scrutins-table thead tr { border-bottom: 2px solid var(--ink); }

	.scrutins-table th {
		text-align: left;
		padding: 10px 14px;
		font-family: var(--font-mono);
		font-size: 11px;
		font-weight: 600;
		color: var(--muted);
		letter-spacing: 0.08em;
		text-transform: uppercase;
	}

	.scrutins-table tbody tr { border-bottom: 1px solid var(--rule); }
	.scrutins-table td { padding: 14px; vertical-align: middle; }

	.num a {
		font-family: var(--font-mono);
		color: var(--accent);
		font-weight: 600;
		text-decoration: none;
	}

	.titre a { color: var(--ink); text-decoration: none; font-family: var(--font-serif); font-size: 17px; }
	.titre a:hover { text-decoration: underline; text-decoration-color: var(--rule); }

	.date { font-family: var(--font-mono); font-size: 12px; color: var(--muted); white-space: nowrap; }
	.bar-cell { min-width: 160px; }

	.vote-num { font-family: var(--font-mono); font-weight: 600; }
	.vote-num.pour   { color: var(--pour); }
	.vote-num.contre { color: var(--contre); }
	.vote-num.abst   { color: var(--abst); }

	.pagination {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 1rem;
		margin-top: 2rem;
	}

	.loading, .empty {
		text-align: center;
		color: var(--muted);
		padding: 2rem;
	}
</style>
