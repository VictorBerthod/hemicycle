<script lang="ts">
	import '../app.css';
	import type { Snippet } from 'svelte';

	let { children }: { children: Snippet } = $props();
	let searchQuery = $state('');

	function handleSearch(e: Event) {
		e.preventDefault();
		if (searchQuery.trim().length >= 2) {
			window.location.href = `/recherche?q=${encodeURIComponent(searchQuery.trim())}`;
		}
	}
</script>

<svelte:head>
	<title>Hemicycle</title>
</svelte:head>

<header>
	<nav class="container">
		<a href="/" class="logo">Hemicycle</a>
		<div class="nav-links">
			<a href="/deputes">Deputes</a>
			<a href="/scrutins">Scrutins</a>
		</div>
		<form class="search-form" onsubmit={handleSearch} role="search">
			<label for="search-input" class="sr-only">Rechercher</label>
			<input
				id="search-input"
				type="search"
				placeholder="Rechercher..."
				bind:value={searchQuery}
			/>
		</form>
	</nav>
</header>

<main class="container">
	{@render children()}
</main>

<footer class="container">
	<p>
		Donnees publiques —
		<a href="https://www.assemblee-nationale.fr" target="_blank" rel="noopener">Assemblee nationale</a>
		| <a href="https://www.civix.fr" target="_blank" rel="noopener">CIVIX</a>
	</p>
</footer>

<style>
	header {
		border-bottom: 1px solid var(--border);
		padding: 0.75rem 0;
		margin-bottom: 2rem;
	}

	nav {
		display: flex;
		align-items: center;
		gap: 1.5rem;
	}

	.logo {
		font-size: 1.3rem;
		font-weight: 700;
		color: var(--text);
	}

	.logo:hover {
		text-decoration: none;
		color: var(--accent);
	}

	.nav-links {
		display: flex;
		gap: 1rem;
	}

	.search-form {
		margin-left: auto;
	}

	.search-form input {
		width: 200px;
	}

	main {
		min-height: 70vh;
		padding-bottom: 3rem;
	}

	footer {
		border-top: 1px solid var(--border);
		padding: 1.5rem 0;
		text-align: center;
		color: var(--text-muted);
		font-size: 0.85rem;
	}
</style>
