<script lang="ts">
	import { getGroupColor } from '$lib/tokens';

	interface Props {
		acronym: string;
		label?: string;
		size?: 'sm' | 'md';
	}

	let { acronym, label, size = 'sm' }: Props = $props();

	let color = $derived(getGroupColor(acronym));
</script>

<span
	class="party-tag"
	class:sm={size === 'sm'}
	class:md={size === 'md'}
	style:border-left="3px solid {color}"
>
	<strong style:color>{acronym}</strong>
	{#if label}
		<span class="lbl">{label}</span>
	{/if}
</span>

<style>
	.party-tag {
		display: inline-flex;
		align-items: center;
		gap: 6px;
		background: var(--paper);
		border: 1px solid var(--rule);
		font-family: var(--font-mono);
		font-weight: 500;
		color: var(--ink);
		letter-spacing: 0.04em;
	}

	.party-tag.sm {
		padding: 2px 8px;
		font-size: 11px;
	}

	.party-tag.md {
		padding: 4px 10px;
		font-size: 13px;
	}

	.party-tag strong {
		font-weight: 600;
	}

	.lbl {
		color: var(--muted);
		font-weight: 400;
	}
</style>
