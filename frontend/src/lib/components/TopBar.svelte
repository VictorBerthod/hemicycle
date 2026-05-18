<script lang="ts">
	/**
	 * TopBar — bande supérieure éditoriale.
	 * Référence : design_handoff_nsv_politique/mockups/mockups/shared.jsx (TopBar).
	 */

	type NavKey = 'accueil' | 'personnalites' | 'scrutins' | 'comparateur' | 'themes' | 'enquetes';

	interface Props {
		active?: NavKey;
		edition?: string;
		onOpenSearch?: () => void;
	}

	let { active, edition, onOpenSearch }: Props = $props();

	const NAV: { key: NavKey; label: string; href: string }[] = [
		{ key: 'accueil', label: 'Accueil', href: '/' },
		{ key: 'personnalites', label: 'Personnalités', href: '/personnalites' },
		{ key: 'scrutins', label: 'Scrutins', href: '/scrutins' },
		{ key: 'comparateur', label: 'Comparateur', href: '/comparateur' },
		{ key: 'themes', label: 'Thèmes', href: '/themes' },
		{ key: 'enquetes', label: 'Enquêtes', href: '/enquetes' },
	];

	function handleSearchClick() {
		if (onOpenSearch) {
			onOpenSearch();
		} else {
			window.location.href = '/recherche';
		}
	}

	function handleSearchKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter' || e.key === ' ') {
			e.preventDefault();
			handleSearchClick();
		}
	}
</script>

<header class="topbar">
	<div class="meta-strip">
		<span>{edition ?? 'Édition n°47 · Semaine du 11 mai 2026'}</span>
		<span class="meta-right">
			<span>17ᵉ législature</span>
			<span class="meta-strong">Open data · MAJ quotidienne</span>
		</span>
	</div>

	<div class="main-row">
		<a class="logo" href="/" aria-label="[PROJET].fr — accueil">
			<span class="logo-name">[PROJET]</span><span class="logo-tld">.fr</span>
		</a>

		<nav aria-label="Navigation principale">
			{#each NAV as item (item.key)}
				<a
					href={item.href}
					class="nav-link"
					class:active={active === item.key}
					aria-current={active === item.key ? 'page' : undefined}
				>
					{item.label}
				</a>
			{/each}
		</nav>

		<div class="actions">
			<div
				class="search-trigger"
				role="button"
				tabindex="0"
				onclick={handleSearchClick}
				onkeydown={handleSearchKeydown}
				aria-label="Ouvrir la recherche"
			>
				<span class="search-icon" aria-hidden="true">⌕</span>
				<span class="search-placeholder">Rechercher un nom, un thème, un scrutin…</span>
				<span class="search-kbd" aria-hidden="true">⌘ K</span>
			</div>
			<a class="subscribe" href="/abonnement">S'abonner</a>
		</div>
	</div>
</header>

<style>
	.topbar {
		background: var(--bg);
		border-bottom: 1px solid var(--ink);
	}

	.meta-strip {
		border-bottom: 1px solid var(--rule);
		padding: 8px var(--page-pad-x);
		display: flex;
		justify-content: space-between;
		align-items: center;
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		color: var(--muted);
	}

	.meta-right {
		display: flex;
		gap: 18px;
	}

	.meta-strong {
		color: var(--ink);
	}

	.main-row {
		display: flex;
		align-items: center;
		padding: 20px var(--page-pad-x);
		gap: 36px;
	}

	.logo {
		font-family: var(--font-serif);
		font-size: 28px;
		font-weight: 600;
		letter-spacing: -0.01em;
		color: var(--ink);
		text-decoration: none;
		flex-shrink: 0;
	}

	.logo:hover {
		text-decoration: none;
	}

	.logo-tld {
		color: var(--accent);
		font-style: italic;
		font-weight: 500;
	}

	nav {
		display: flex;
		gap: 24px;
		margin-left: 20px;
	}

	.nav-link {
		font-family: var(--font-sans);
		font-size: 15px;
		font-weight: 500;
		color: var(--ink);
		text-decoration: none;
		border-bottom: 2px solid transparent;
		padding-bottom: 4px;
		transition: border-color 0.15s, color 0.15s;
	}

	.nav-link:hover {
		border-bottom-color: var(--rule);
		text-decoration: none;
	}

	.nav-link.active {
		color: var(--accent);
		border-bottom-color: var(--accent);
	}

	.actions {
		margin-left: auto;
		display: flex;
		gap: 12px;
		align-items: center;
	}

	.search-trigger {
		display: flex;
		align-items: center;
		gap: 8px;
		background: var(--paper);
		border: 1px solid var(--rule);
		padding: 7px 12px;
		min-width: 280px;
		font-family: var(--font-mono);
		font-size: 13px;
		color: var(--muted);
		cursor: pointer;
		transition: border-color 0.15s;
	}

	.search-trigger:hover {
		border-color: var(--ink);
	}

	.search-trigger:focus-visible {
		outline: 2px solid var(--ink);
		outline-offset: 2px;
	}

	.search-icon {
		font-size: 15px;
	}

	.search-placeholder {
		flex: 1;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.search-kbd {
		font-size: 10px;
		padding: 1px 5px;
		background: var(--bg-alt);
		border: 1px solid var(--rule);
		color: var(--muted);
	}

	.subscribe {
		background: var(--ink);
		color: var(--bg);
		text-decoration: none;
		padding: 9px 16px;
		font-family: var(--font-mono);
		font-size: 12px;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		font-weight: 600;
	}

	.subscribe:hover {
		text-decoration: none;
		opacity: 0.85;
	}

	@media (max-width: 1024px) {
		nav {
			gap: 16px;
			margin-left: 8px;
		}
		.search-trigger {
			min-width: 200px;
		}
	}

	@media (max-width: 768px) {
		.main-row {
			flex-wrap: wrap;
			gap: 16px;
		}
		nav {
			order: 3;
			width: 100%;
			margin-left: 0;
			overflow-x: auto;
		}
		.actions {
			margin-left: auto;
		}
		.search-trigger {
			min-width: 0;
		}
		.search-placeholder {
			display: none;
		}
	}
</style>
