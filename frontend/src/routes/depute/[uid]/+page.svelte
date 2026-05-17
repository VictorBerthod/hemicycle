<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { getDepute, getDissidences, type DeputeDetail, type DissidenceResult } from '$lib/api';

	let depute = $state<DeputeDetail | null>(null);
	let dissidences = $state<DissidenceResult | null>(null);
	let error = $state('');
	let uid = $derived($page.params.uid!);

	onMount(async () => {
		try {
			const [d, diss] = await Promise.all([
				getDepute(uid),
				getDissidences(uid),
			]);
			depute = d;
			dissidences = diss;
		} catch {
			error = 'Depute non trouve.';
		}
	});
</script>

<svelte:head>
	{#if depute}
		<title>{depute.prenom} {depute.nom} — Hemicycle</title>
		<meta property="og:title" content="{depute.prenom} {depute.nom} — Hemicycle" />
		<meta property="og:description" content="Fiche du depute {depute.prenom} {depute.nom}, {depute.groupe?.nom || 'non-inscrit'}" />
	{/if}
</svelte:head>

{#if error}
	<p class="error">{error}</p>
	<a href="/deputes">Retour a la liste</a>
{:else if depute}
	<div class="depute-header">
		<img
			src={depute.photo_url || ''}
			alt="{depute.prenom} {depute.nom}"
			class="photo"
			onerror={(e) => { (e.target as HTMLImageElement).style.display = 'none'; }}
		/>
		<div class="header-info">
			<h1>{depute.prenom} {depute.nom}</h1>
			{#if depute.groupe}
				<p class="groupe">{depute.groupe.acronyme} — {depute.groupe.nom}</p>
			{:else}
				<p class="groupe">Non inscrit</p>
			{/if}
			{#if depute.circo_departement}
				<p class="meta">{depute.circo_departement}, {depute.circo_numero}e circonscription</p>
			{/if}
			{#if depute.url_an}
				<p><a href={depute.url_an} target="_blank" rel="noopener">Voir sur assemblee-nationale.fr</a></p>
			{/if}
		</div>
	</div>

	{#if dissidences && dissidences.total_votes > 0}
		<section class="dissidence-section">
			<h2>Discipline de vote</h2>
			<div class="dissidence-bar">
				<div class="aligned" style="width: {100 - dissidences.taux_dissidence}%"></div>
				<div class="dissident" style="width: {dissidences.taux_dissidence}%"></div>
			</div>
			<p class="dissidence-stats">
				{dissidences.taux_dissidence}% de dissidence
				({dissidences.dissidences.length} vote{dissidences.dissidences.length > 1 ? 's' : ''} sur {dissidences.total_votes} contre la majorite du groupe)
			</p>
			{#if dissidences.dissidences.length > 0}
				<ul class="dissidence-list">
					{#each dissidences.dissidences as d}
						<li class="card">
							<a href="/scrutin/{d.scrutin_numero}">{d.scrutin_titre}</a>
							<span class="dissidence-detail">
								A vote <span class="badge badge-{d.depute_position}">{d.depute_position}</span>
								(groupe : <span class="badge badge-{d.groupe_position}">{d.groupe_position}</span>)
							</span>
							<span class="vote-date">{d.scrutin_date}</span>
						</li>
					{/each}
				</ul>
			{/if}
		</section>
	{/if}

	<section class="votes-section">
		<h2>Derniers votes</h2>
		{#if depute.recent_votes.length === 0}
			<p class="empty">Aucun vote enregistre.</p>
		{:else}
			<ul class="votes-list">
				{#each depute.recent_votes as vote}
					<li class="card vote-item">
						<div class="vote-info">
							<a href="/scrutin/{vote.scrutin_numero}">{vote.scrutin_titre}</a>
							<span class="vote-date">{vote.scrutin_date}</span>
						</div>
						<div class="vote-position">
							<span class="badge badge-{vote.position}">{vote.position}</span>
							<span class="badge badge-{vote.scrutin_sort}">{vote.scrutin_sort}</span>
						</div>
					</li>
				{/each}
			</ul>
		{/if}
	</section>
{:else}
	<p class="loading">Chargement...</p>
{/if}

<style>
	.depute-header {
		display: flex;
		gap: 1.5rem;
		align-items: flex-start;
		margin-bottom: 2rem;
	}

	.photo {
		width: 120px;
		height: 120px;
		border-radius: 50%;
		object-fit: cover;
		background: var(--border);
	}

	.header-info h1 {
		margin-bottom: 0.25rem;
	}

	.groupe {
		color: var(--accent);
		font-size: 1rem;
	}

	.meta {
		color: var(--text-muted);
		font-size: 0.9rem;
	}

	h2 {
		margin-bottom: 1rem;
	}

	.votes-list {
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.vote-item {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 1rem;
	}

	.vote-info {
		flex: 1;
	}

	.vote-info a {
		display: block;
		font-size: 0.95rem;
	}

	.vote-date {
		font-size: 0.8rem;
		color: var(--text-muted);
	}

	.vote-position {
		display: flex;
		gap: 0.5rem;
	}

	.dissidence-section {
		margin-bottom: 2rem;
	}

	.dissidence-bar {
		display: flex;
		height: 8px;
		border-radius: 4px;
		overflow: hidden;
		background: var(--border);
		margin: 0.5rem 0;
	}

	.dissidence-bar .aligned {
		background: var(--pour);
	}

	.dissidence-bar .dissident {
		background: var(--contre);
	}

	.dissidence-stats {
		font-size: 0.9rem;
		color: var(--text-muted);
		margin-bottom: 1rem;
	}

	.dissidence-list {
		list-style: none;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.dissidence-list li {
		display: flex;
		flex-direction: column;
		gap: 0.25rem;
	}

	.dissidence-detail {
		font-size: 0.85rem;
	}

	.loading, .empty, .error {
		text-align: center;
		color: var(--text-muted);
		padding: 2rem;
	}

	.error {
		color: var(--contre);
	}
</style>
