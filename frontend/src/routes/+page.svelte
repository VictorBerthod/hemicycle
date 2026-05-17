<script lang="ts">
	import { onMount } from 'svelte';
	import { getStats, type Stats } from '$lib/api';

	let stats = $state<Stats | null>(null);
	let error = $state('');

	onMount(async () => {
		try {
			stats = await getStats();
		} catch (e) {
			error = 'Impossible de charger les statistiques. Le backend est-il lance ?';
		}
	});
</script>

<svelte:head>
	<title>Hemicycle — L'Assemblee mise a nu</title>
	<meta name="description" content="Qui vote quoi a l'Assemblee nationale. Donnees publiques, angles engages." />
</svelte:head>

<section class="hero">
	<h1>L'Assemblee mise a nu</h1>
	<p class="subtitle">Qui vote quoi, qui sert qui. Donnees publiques, angles engages.</p>

	{#if stats}
		<div class="stats-grid">
			<div class="stat-card card">
				<span class="stat-number">{stats.total_deputes}</span>
				<span class="stat-label">deputes</span>
			</div>
			<div class="stat-card card">
				<span class="stat-number">{stats.total_scrutins.toLocaleString('fr-FR')}</span>
				<span class="stat-label">scrutins</span>
			</div>
			<div class="stat-card card">
				<span class="stat-number">{stats.total_votes.toLocaleString('fr-FR')}</span>
				<span class="stat-label">votes enregistres</span>
			</div>
			<div class="stat-card card">
				<span class="stat-number">{stats.total_groupes}</span>
				<span class="stat-label">groupes</span>
			</div>
		</div>
	{/if}

	{#if error}
		<p class="error">{error}</p>
	{/if}

	<div class="cta-links">
		<a href="/deputes" class="cta">Explorer les deputes</a>
		<a href="/scrutins" class="cta">Voir les scrutins</a>
	</div>
</section>

<style>
	.hero {
		text-align: center;
		padding: 3rem 0;
	}

	h1 {
		font-size: 2.5rem;
		margin-bottom: 0.5rem;
	}

	.subtitle {
		color: var(--text-muted);
		font-size: 1.1rem;
		margin-bottom: 2rem;
	}

	.stats-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
		gap: 1rem;
		margin-bottom: 2rem;
	}

	.stat-card {
		text-align: center;
		padding: 1.5rem 1rem;
	}

	.stat-number {
		display: block;
		font-size: 2rem;
		font-weight: 700;
		color: var(--accent);
	}

	.stat-label {
		color: var(--text-muted);
		font-size: 0.85rem;
	}

	.cta-links {
		display: flex;
		gap: 1rem;
		justify-content: center;
	}

	.cta {
		padding: 0.75rem 1.5rem;
		background: var(--accent);
		color: #000;
		border-radius: var(--radius);
		font-weight: 600;
	}

	.cta:hover {
		text-decoration: none;
		opacity: 0.9;
	}

	.error {
		color: var(--contre);
		margin: 1rem 0;
	}
</style>
