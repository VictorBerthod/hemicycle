<script lang="ts">
	import { search, type SearchResult } from '$lib/api';
	import { getGroupColor } from '$lib/tokens';

	interface Props {
		open: boolean;
		onClose: () => void;
	}

	let { open, onClose }: Props = $props();

	let query = $state('');
	let results = $state<SearchResult | null>(null);
	let loading = $state(false);
	let selectedIndex = $state(-1);

	let inputEl = $state<HTMLInputElement | null>(null);
	let debounceTimer: ReturnType<typeof setTimeout>;

	// Focus input when modal opens
	$effect(() => {
		if (open) {
			query = '';
			results = null;
			selectedIndex = -1;
			// Wait for DOM
			setTimeout(() => inputEl?.focus(), 10);
		}
	});

	async function handleInput() {
		selectedIndex = -1;
		clearTimeout(debounceTimer);
		if (query.length < 2) {
			results = null;
			return;
		}
		debounceTimer = setTimeout(async () => {
			loading = true;
			try {
				results = await search(query);
			} catch {
				results = { deputes: [], scrutins: [] };
			} finally {
				loading = false;
			}
		}, 220);
	}

	let allItems = $derived(() => {
		if (!results) return [];
		return [
			...results.deputes.slice(0, 5).map(d => ({
				type: 'depute' as const,
				key: d.uid,
				label: `${d.prenom} ${d.nom}`,
				sub: d.groupe?.acronyme ?? '',
				href: `/personnalite/${d.uid}`,
			})),
			...results.scrutins.slice(0, 5).map(s => ({
				type: 'scrutin' as const,
				key: String(s.id),
				label: s.titre,
				sub: `n°${s.numero} · ${s.date_scrutin}`,
				href: `/scrutin/${s.numero}`,
			})),
		];
	});

	function handleKeydown(e: KeyboardEvent) {
		const items = allItems();
		if (e.key === 'Escape') {
			onClose();
		} else if (e.key === 'ArrowDown') {
			e.preventDefault();
			selectedIndex = Math.min(selectedIndex + 1, items.length - 1);
		} else if (e.key === 'ArrowUp') {
			e.preventDefault();
			selectedIndex = Math.max(selectedIndex - 1, 0);
		} else if (e.key === 'Enter' && selectedIndex >= 0) {
			e.preventDefault();
			window.location.href = items[selectedIndex].href;
		}
	}

	function handleBackdropClick(e: MouseEvent) {
		if (e.target === e.currentTarget) onClose();
	}
</script>

{#if open}
<div
	class="backdrop"
	role="dialog"
	aria-label="Recherche rapide"
	aria-modal="true"
	tabindex="-1"
	onclick={handleBackdropClick}
	onkeydown={handleKeydown}
>
	<div class="modal">
		<!-- Search input -->
		<div class="search-row">
			<span class="search-icon" aria-hidden="true">⌕</span>
			<input
				bind:this={inputEl}
				bind:value={query}
				oninput={handleInput}
				type="search"
				placeholder="Rechercher un nom, un scrutin, un thème…"
				autocomplete="off"
				aria-label="Recherche"
				aria-controls="cmd-results"
				aria-autocomplete="list"
			/>
			<button class="close-btn" onclick={onClose} aria-label="Fermer">
				<span aria-hidden="true">Esc</span>
			</button>
		</div>

		<!-- Results -->
		<div id="cmd-results" role="listbox" aria-label="Résultats de recherche">
			{#if query.length < 2}
				<div class="hint">
					<span>Tapez au moins 2 caractères…</span>
					<div class="shortcuts">
						<span><kbd>↑</kbd><kbd>↓</kbd> naviguer</span>
						<span><kbd>↵</kbd> ouvrir</span>
						<span><kbd>Esc</kbd> fermer</span>
					</div>
				</div>
			{:else if loading}
				<div class="hint">Recherche en cours…</div>
			{:else if results && allItems().length === 0}
				<div class="hint">Aucun résultat pour « {query} ».</div>
			{:else if results}
				{@const items = allItems()}
				{#if results.deputes.length > 0}
					<div class="group-label" aria-hidden="true">Personnalités</div>
				{/if}
				{#each items as item, i (item.key + item.type)}
					<a
						href={item.href}
						class="result-item"
						class:active={i === selectedIndex}
						role="option"
						aria-selected={i === selectedIndex}
						onclick={onClose}
						tabindex="-1"
					>
						{#if item.type === 'depute'}
							<span class="result-icon" aria-hidden="true">
								<span class="group-dot" style:background={getGroupColor(item.sub)}></span>
							</span>
						{:else}
							<span class="result-icon result-icon-scrutin" aria-hidden="true">§</span>
						{/if}
						<span class="result-label">{item.label}</span>
						<span class="result-sub">{item.sub}</span>
					</a>
					{#if item.type === 'depute' && i === results.deputes.slice(0, 5).length - 1 && results.scrutins.length > 0}
						<div class="group-label" aria-hidden="true">Scrutins</div>
					{/if}
				{/each}
			{/if}
		</div>

		<div class="footer-bar">
			<span>Recherche par <a href="/recherche?q={encodeURIComponent(query)}" onclick={onClose}>recherche avancée →</a></span>
		</div>
	</div>
</div>
{/if}

<style>
	.backdrop {
		position: fixed;
		inset: 0;
		background: rgba(26, 26, 26, 0.55);
		display: flex;
		align-items: flex-start;
		justify-content: center;
		padding-top: clamp(48px, 10vh, 120px);
		z-index: 1000;
	}

	@media (prefers-reduced-motion: no-preference) {
		.backdrop { animation: fade-in 0.12s ease; }
		.modal { animation: slide-in 0.15s ease; }
	}

	@keyframes fade-in {
		from { opacity: 0; }
		to   { opacity: 1; }
	}

	@keyframes slide-in {
		from { transform: translateY(-8px); opacity: 0; }
		to   { transform: translateY(0);    opacity: 1; }
	}

	.modal {
		background: var(--paper);
		border: 1px solid var(--ink);
		width: 100%;
		max-width: 640px;
		margin: 0 16px;
		display: flex;
		flex-direction: column;
	}

	/* Search input row */
	.search-row {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 16px 20px;
		border-bottom: 1px solid var(--rule);
	}

	.search-icon {
		font-size: 18px;
		color: var(--muted);
		flex-shrink: 0;
	}

	.search-row input {
		flex: 1;
		background: transparent;
		border: none;
		outline: none;
		font-family: var(--font-sans);
		font-size: 17px;
		color: var(--ink);
	}

	.search-row input::placeholder { color: var(--muted); }

	.close-btn {
		background: var(--bg-alt);
		border: 1px solid var(--rule);
		padding: 3px 8px;
		font-family: var(--font-mono);
		font-size: 10px;
		letter-spacing: 0.06em;
		color: var(--muted);
		cursor: pointer;
		flex-shrink: 0;
	}

	/* Results list */
	[role="listbox"] {
		max-height: 380px;
		overflow-y: auto;
	}

	.group-label {
		padding: 8px 20px 4px;
		font-family: var(--font-mono);
		font-size: 10px;
		letter-spacing: 0.1em;
		text-transform: uppercase;
		color: var(--muted);
		background: var(--bg-alt);
		border-bottom: 1px solid var(--rule);
	}

	.result-item {
		display: flex;
		align-items: center;
		gap: 12px;
		padding: 12px 20px;
		border-bottom: 1px solid var(--rule);
		text-decoration: none;
		color: var(--ink);
		transition: background 0.08s;
	}

	.result-item:hover,
	.result-item.active {
		background: var(--bg-alt);
	}

	.result-icon {
		width: 24px;
		display: flex;
		align-items: center;
		justify-content: center;
		flex-shrink: 0;
	}

	.result-icon-scrutin {
		font-family: var(--font-mono);
		font-size: 13px;
		color: var(--accent);
		font-weight: 600;
	}

	.group-dot {
		width: 10px;
		height: 10px;
		border-radius: 50%;
		display: block;
	}

	.result-label {
		flex: 1;
		font-family: var(--font-serif);
		font-size: 16px;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.result-sub {
		font-family: var(--font-mono);
		font-size: 11px;
		color: var(--muted);
		letter-spacing: 0.04em;
		flex-shrink: 0;
	}

	/* Hint / empty */
	.hint {
		padding: 24px 20px;
		font-size: 14px;
		color: var(--muted);
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 12px;
	}

	.shortcuts {
		display: flex;
		gap: 16px;
		font-family: var(--font-mono);
		font-size: 11px;
		color: var(--muted);
	}

	kbd {
		display: inline-block;
		padding: 1px 5px;
		background: var(--bg-alt);
		border: 1px solid var(--rule);
		font-family: var(--font-mono);
		font-size: 10px;
		border-radius: 2px;
	}

	/* Footer */
	.footer-bar {
		padding: 10px 20px;
		border-top: 1px solid var(--rule);
		font-family: var(--font-mono);
		font-size: 11px;
		color: var(--muted);
	}

	.footer-bar a { color: var(--accent); text-decoration: none; }
	.footer-bar a:hover { text-decoration: underline; }
</style>
