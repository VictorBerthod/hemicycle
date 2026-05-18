<script lang="ts">
	import type { Snippet } from 'svelte';

	type BadgePosition = 'pour' | 'contre' | 'abst' | 'absent' | 'adopte' | 'rejete';

	interface Props {
		position: BadgePosition;
		children?: Snippet;
	}

	let { position, children }: Props = $props();

	const MAP: Record<BadgePosition, { bg: string; fg: string; label: string; border?: string }> = {
		pour:   { bg: 'var(--pour)',   fg: '#fff', label: 'Pour' },
		contre: { bg: 'var(--contre)', fg: '#fff', label: 'Contre' },
		abst:   { bg: 'var(--abst)',   fg: '#fff', label: 'Abstention' },
		absent: { bg: 'transparent',   fg: 'var(--muted)', label: 'Absent', border: '1px dashed var(--muted)' },
		adopte: { bg: 'var(--pour)',   fg: '#fff', label: 'Adopté' },
		rejete: { bg: 'var(--contre)', fg: '#fff', label: 'Rejeté' },
	};

	let s = $derived(MAP[position] ?? MAP.absent);
</script>

<span
	class="vote-badge"
	style:background={s.bg}
	style:color={s.fg}
	style:border={s.border ?? 'none'}
>
	{#if children}
		{@render children()}
	{:else}
		{s.label}
	{/if}
</span>

<style>
	.vote-badge {
		display: inline-block;
		padding: 3px 10px;
		font-family: var(--font-mono);
		font-size: 11px;
		letter-spacing: 0.08em;
		text-transform: uppercase;
		font-weight: 600;
		line-height: 1.4;
	}
</style>
