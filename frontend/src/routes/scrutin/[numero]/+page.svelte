<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { getScrutin, type ScrutinDetail } from '$lib/api';

	let scrutin = $state<ScrutinDetail | null>(null);
	let error = $state('');
	let numero = $derived(Number($page.params.numero));

	onMount(async () => {
		try {
			scrutin = await getScrutin(numero);
		} catch {
			error = 'Scrutin non trouve.';
		}
	});

	let votesByPosition = $derived.by(() => {
		if (!scrutin) return { pour: [], contre: [], abstention: [] };
		const grouped: Record<string, typeof scrutin.votes> = { pour: [], contre: [], abstention: [] };
		for (const v of scrutin.votes) {
			(grouped[v.position] ??= []).push(v);
		}
		return grouped;
	});
</script>

<svelte:head>
	{#if scrutin}
		<title>Scrutin n{scrutin.numero} — Hemicycle</title>
		<meta property="og:title" content="Scrutin n{scrutin.numero} — Hemicycle" />
		<meta property="og:description" content="{scrutin.titre} — {scrutin.sort}" />
	{/if}
</svelte:head>

{#if error}
	<p class="error">{error}</p>
	<a href="/scrutins">Retour aux scrutins</a>
{:else if scrutin}
	<a href="/scrutins" class="back">Retour aux scrutins</a>

	<div class="scrutin-header">
		<h1>Scrutin n{scrutin.numero}</h1>
		<span class="badge badge-{scrutin.sort}">{scrutin.sort}</span>
	</div>

	<p class="titre">{scrutin.titre}</p>
	<p class="date">Vote du {scrutin.date_scrutin}</p>

	{#if scrutin.nb_votants > 0}
		<div class="results-summary">
			<div class="vote-bar" role="img" aria-label="{scrutin.nb_pour} pour, {scrutin.nb_contre} contre, {scrutin.nb_abstention} abstentions">
				<div class="pour" style="width: {(scrutin.nb_pour / (scrutin.nb_pour + scrutin.nb_contre + scrutin.nb_abstention)) * 100}%"></div>
				<div class="contre" style="width: {(scrutin.nb_contre / (scrutin.nb_pour + scrutin.nb_contre + scrutin.nb_abstention)) * 100}%"></div>
				<div class="abstention" style="width: {(scrutin.nb_abstention / (scrutin.nb_pour + scrutin.nb_contre + scrutin.nb_abstention)) * 100}%"></div>
			</div>
			<div class="vote-numbers">
				<span class="pour-num">{scrutin.nb_pour} pour</span>
				<span class="contre-num">{scrutin.nb_contre} contre</span>
				<span class="abst-num">{scrutin.nb_abstention} abstentions</span>
			</div>
		</div>
	{/if}

	{#if scrutin.votes.length > 0}
		<div class="votes-detail">
			{#each ['pour', 'contre', 'abstention'] as position}
				{@const votes = votesByPosition[position] || []}
				{#if votes.length > 0}
					<section>
						<h2 class="position-header position-{position}">
							{position} ({votes.length})
						</h2>
						<ul class="vote-list">
							{#each votes as v}
								<li>
									<a href="/depute/{v.depute_uid}">
										{v.depute_prenom} {v.depute_nom}
									</a>
									{#if v.groupe_acronyme}
										<span class="groupe-tag">{v.groupe_acronyme}</span>
									{/if}
								</li>
							{/each}
						</ul>
					</section>
				{/if}
			{/each}
		</div>
	{:else}
		<p class="empty">Detail des votes non disponible pour ce scrutin.</p>
	{/if}

	<p class="source">
		Source :
		<a href="https://www.assemblee-nationale.fr/dyn/17/scrutins/{scrutin.numero}" target="_blank" rel="noopener">
			assemblee-nationale.fr
		</a>
	</p>
{:else}
	<p class="loading">Chargement...</p>
{/if}

<style>
	.back {
		display: inline-block;
		margin-bottom: 1rem;
		font-size: 0.9rem;
	}

	.scrutin-header {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-bottom: 0.5rem;
	}

	h1 { font-size: 1.8rem; }

	.titre {
		font-size: 1.1rem;
		margin-bottom: 0.25rem;
	}

	.date {
		color: var(--text-muted);
		font-size: 0.9rem;
		margin-bottom: 1.5rem;
	}

	.results-summary {
		margin-bottom: 2rem;
	}

	.vote-numbers {
		display: flex;
		gap: 1.5rem;
		margin-top: 0.5rem;
		font-size: 0.95rem;
	}

	.pour-num { color: var(--pour); }
	.contre-num { color: var(--contre); }
	.abst-num { color: var(--abstention); }

	.votes-detail {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 1.5rem;
		margin-bottom: 2rem;
	}

	.position-header {
		font-size: 1.1rem;
		margin-bottom: 0.75rem;
		padding-bottom: 0.25rem;
		border-bottom: 2px solid;
	}

	.position-pour { border-color: var(--pour); color: var(--pour); }
	.position-contre { border-color: var(--contre); color: var(--contre); }
	.position-abstention { border-color: var(--abstention); color: var(--abstention); }

	.vote-list {
		list-style: none;
		font-size: 0.9rem;
	}

	.vote-list li {
		padding: 0.25rem 0;
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.groupe-tag {
		font-size: 0.75rem;
		color: var(--text-muted);
	}

	.source {
		font-size: 0.85rem;
		color: var(--text-muted);
		margin-top: 2rem;
	}

	.loading, .empty, .error {
		text-align: center;
		color: var(--text-muted);
		padding: 2rem;
	}

	.error { color: var(--contre); }
</style>
