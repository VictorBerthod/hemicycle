<script lang="ts">
	import '../app.css';
	import type { Snippet } from 'svelte';
	import { page } from '$app/state';
	import TopBar from '$lib/components/TopBar.svelte';
	import Footer from '$lib/components/Footer.svelte';
	import CommandK from '$lib/components/CommandK.svelte';

	let { children }: { children: Snippet } = $props();

	type NavKey = 'accueil' | 'personnalites' | 'scrutins' | 'comparateur' | 'themes' | 'enquetes';

	function routeToNavKey(path: string): NavKey | undefined {
		if (path === '/') return 'accueil';
		if (path.startsWith('/personnalites') || path.startsWith('/personnalite/')) return 'personnalites';
		if (path.startsWith('/deputes') || path.startsWith('/depute/')) return 'personnalites';
		if (path.startsWith('/scrutins') || path.startsWith('/scrutin/')) return 'scrutins';
		if (path.startsWith('/comparateur')) return 'comparateur';
		if (path.startsWith('/themes')) return 'themes';
		if (path.startsWith('/enquetes')) return 'enquetes';
		return undefined;
	}

	let active = $derived(routeToNavKey(page.url.pathname));
	let searchOpen = $state(false);

	function openSearch() { searchOpen = true; }
	function closeSearch() { searchOpen = false; }

	function handleGlobalKeydown(e: KeyboardEvent) {
		if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
			e.preventDefault();
			searchOpen = !searchOpen;
		}
	}
</script>

<svelte:head>
	<title>[PROJET].fr — Transparence parlementaire</title>
</svelte:head>

<svelte:window onkeydown={handleGlobalKeydown} />

<div class="layout">
	<TopBar {active} onOpenSearch={openSearch} />

	<main>
		{@render children()}
	</main>

	<Footer />
</div>

<CommandK open={searchOpen} onClose={closeSearch} />

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
