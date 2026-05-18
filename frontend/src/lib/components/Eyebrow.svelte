<script lang="ts">
	import type { Snippet } from 'svelte';

	interface Props {
		children?: Snippet;
	}

	let { children }: Props = $props();
</script>

<div class="eyebrow">
	<span class="line" aria-hidden="true"></span>
	{#if children}{@render children()}{/if}
</div>

<style>
	.eyebrow {
		display: flex;
		align-items: center;
		gap: 14px;
		font-family: var(--font-mono);
		font-size: 12px;
		letter-spacing: 0.14em;
		text-transform: uppercase;
		color: var(--accent);
	}

	.line {
		display: inline-block;
		width: 28px;
		height: 1px;
		background: var(--accent);
		flex-shrink: 0;
	}
</style>
