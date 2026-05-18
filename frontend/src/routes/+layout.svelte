<script lang="ts">
	import '../app.css';
	import type { Snippet } from 'svelte';
	import { page } from '$app/state';
	import TopBar from '$lib/components/TopBar.svelte';
	import Footer from '$lib/components/Footer.svelte';

	let { children }: { children: Snippet } = $props();

	type NavKey = 'accueil' | 'personnalites' | 'scrutins' | 'comparateur' | 'themes' | 'enquetes';

	function routeToNavKey(path: string): NavKey | undefined {
		if (path === '/') return 'accueil';
		if (path.startsWith('/personnalites') || path.startsWith('/personnalite/')) return 'personnalites';
		// Compat anciens chemins /deputes /depute/[uid]
		if (path.startsWith('/deputes') || path.startsWith('/depute/')) return 'personnalites';
		if (path.startsWith('/scrutins') || path.startsWith('/scrutin/')) return 'scrutins';
		if (path.startsWith('/comparateur')) return 'comparateur';
		if (path.startsWith('/themes')) return 'themes';
		if (path.startsWith('/enquetes')) return 'enquetes';
		return undefined;
	}

	let active = $derived(routeToNavKey(page.url.pathname));
</script>

<svelte:head>
	<title>[PROJET].fr — Transparence parlementaire</title>
</svelte:head>

<div class="layout">
	<TopBar {active} />

	<main>
		{@render children()}
	</main>

	<Footer />
</div>

<style>
	.layout {
		min-height: 100vh;
		display: flex;
		flex-direction: column;
	}

	main {
		flex: 1;
	}
</style>
